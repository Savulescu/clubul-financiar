-- =============================================================================
-- schema_analytics.sql — statistici complete Clubul Financiar (cookieless, GDPR-safe)
-- Rulează O DATĂ în Supabase: Dashboard → SQL Editor → New query → paste → Run.
-- Extinde sistemul vechi (page_views + cf_stats) FĂRĂ să-l strice: păstrează
-- istoricul de vizitatori de la 19 iun 2026 și adaugă pagini+timp, surse, interes
-- pe abonamente, newsletter și orice eveniment de pe site.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1) page_views — primește o coloană `source` (cum ne-au găsit). Tabelul există deja.
-- -----------------------------------------------------------------------------
alter table public.page_views add column if not exists source text;

-- -----------------------------------------------------------------------------
-- 2) cf_events — jurnal append-only cu TOT ce face vizitatorul (event-sourced).
--    type:    pageview | page_time | scroll | tier_view | tier_click |
--             cta_click | search | tool_use | quiz | signup | ai_ask | ...
--    seconds: pentru page_time = timpul ACTIV cumulat pe pagină (heartbeat)
--    depth:   pentru scroll = adâncimea maximă în %
--    tier:    pentru tier_view/tier_click = free|premium|pro|ultra|...
-- -----------------------------------------------------------------------------
create table if not exists public.cf_events (
  id        bigint generated always as identity primary key,
  ts        timestamptz not null default now(),
  type      text not null,
  path      text,
  visitor   text,                 -- id persistent (localStorage) = vizitator unic
  session   text,                 -- id per-vizită (sessionStorage) = o sesiune
  referrer  text,
  source    text,                 -- normalizat: direct|google|facebook|utm... (first-touch pe sesiune)
  tier      text,
  seconds   integer,
  depth     integer,
  meta      jsonb
);
create index if not exists cf_events_ts_idx       on public.cf_events (ts);
create index if not exists cf_events_type_ts_idx  on public.cf_events (type, ts);
create index if not exists cf_events_sess_idx     on public.cf_events (session);
-- TODO scalare: heartbeat-ul de timp pe pagină generează ~1 rând/15s/vizită.
-- La trafic mare, adaugă un tabel de rollup zilnic + cron pg_cron care agregă
-- cf_events vechi în cf_daily și șterge rândurile brute > 90 zile.

alter table public.cf_events enable row level security;

-- oricine poate INSERA un eveniment (anon key, fără date personale), dar
-- NIMENI nu poate citi rândurile direct — citirea e doar prin cf_stats_full (admin).
drop policy if exists "cf insert events" on public.cf_events;
create policy "cf insert events" on public.cf_events
  for insert to anon, authenticated with check (true);

-- -----------------------------------------------------------------------------
-- 3) cf_stats_full(p_days) — un singur RPC care întoarce TOT pentru panou.
--    Doar pentru admin (clubulfinanciar@gmail.com). p_days = fereastra pentru
--    secțiunile detaliate (top pagini, surse, abonamente, evenimente).
--    Folosește 100000 pentru „total / de la start".
-- -----------------------------------------------------------------------------
create or replace function public.cf_stats_full(p_days integer default 30)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  email text := (auth.jwt() ->> 'email');
  since timestamptz := now() - (greatest(p_days, 1) || ' days')::interval;
  res jsonb;
begin
  if email is null or lower(email) <> 'clubulfinanciar@gmail.com' then
    raise exception 'forbidden';
  end if;

  res := jsonb_build_object(
    'window_days', p_days,

    -- a) Vizitatori pe intervale (continuitate din page_views, de la instalare)
    'ranges', (
      select jsonb_build_object(
        'h24',  jsonb_build_object('views', count(*) filter (where ts > now()-interval '24 hours'),
                                   'visitors', count(distinct visitor) filter (where ts > now()-interval '24 hours')),
        'd7',   jsonb_build_object('views', count(*) filter (where ts > now()-interval '7 days'),
                                   'visitors', count(distinct visitor) filter (where ts > now()-interval '7 days')),
        'd30',  jsonb_build_object('views', count(*) filter (where ts > now()-interval '30 days'),
                                   'visitors', count(distinct visitor) filter (where ts > now()-interval '30 days')),
        'd90',  jsonb_build_object('views', count(*) filter (where ts > now()-interval '90 days'),
                                   'visitors', count(distinct visitor) filter (where ts > now()-interval '90 days')),
        'd180', jsonb_build_object('views', count(*) filter (where ts > now()-interval '180 days'),
                                   'visitors', count(distinct visitor) filter (where ts > now()-interval '180 days')),
        'd365', jsonb_build_object('views', count(*) filter (where ts > now()-interval '365 days'),
                                   'visitors', count(distinct visitor) filter (where ts > now()-interval '365 days')),
        'total',jsonb_build_object('views', count(*), 'visitors', count(distinct visitor))
      ) from public.page_views
    ),

    -- b) Top pagini: afișări, vizitatori unici și TIMP MEDIU pe pagină (sec).
    --    Timpul = media pe sesiune a maximului de secunde active raportate (cumulativ).
    'top_pages', (
      select coalesce(jsonb_agg(t order by t.views desc), '[]'::jsonb) from (
        select pv.path as path,
               count(*) as views,
               count(distinct pv.visitor) as visitors,
               coalesce((
                 select round(avg(mx))::int from (
                   select max(e.seconds) as mx
                   from public.cf_events e
                   where e.type = 'page_time' and e.path = pv.path
                     and e.ts > since and e.seconds between 1 and 7200
                   group by e.session
                 ) q
               ), 0) as avg_seconds
        from public.page_views pv
        where pv.ts > since
        group by pv.path
        order by views desc
        limit 60
      ) t
    ),

    -- c) Cum ne-au găsit (surse de trafic)
    'sources', (
      select coalesce(jsonb_agg(s order by s.visitors desc), '[]'::jsonb) from (
        select coalesce(nullif(source, ''), 'direct') as source,
               count(distinct visitor) as visitors,
               count(*) as views
        from public.page_views
        where ts > since
        group by 1
        order by visitors desc
        limit 40
      ) s
    ),

    -- d) Interes pe abonamente (cine s-a uitat / a dat click pe fiecare plan)
    'tiers', (
      select coalesce(jsonb_object_agg(z.tier, z.obj), '{}'::jsonb) from (
        select tier,
               jsonb_build_object(
                 'views',   count(*) filter (where type = 'tier_view'),
                 'viewers', count(distinct session) filter (where type = 'tier_view'),
                 'clicks',  count(*) filter (where type = 'tier_click')
               ) as obj
        from public.cf_events
        where tier is not null and ts > since and type in ('tier_view', 'tier_click')
        group by tier
      ) z
    ),

    -- e) Newsletter (abonați)
    'newsletter', (
      select jsonb_build_object(
        'total',  count(*),
        'active', count(*) filter (where subscribed),
        'last7',  count(*) filter (where created_at > now()-interval '7 days'),
        'last30', count(*) filter (where created_at > now()-interval '30 days')
      ) from public.newsletter_subscribers
    ),

    -- f) Defalcare evenimente (tot ce s-a întâmplat pe site, pe tipuri)
    'events', (
      select coalesce(jsonb_agg(e order by e.count desc), '[]'::jsonb) from (
        select type, count(*) as count
        from public.cf_events
        where ts > since
        group by type
        order by count desc
      ) e
    ),

    -- g) Implicare generală
    'engagement', (
      select jsonb_build_object(
        'avg_seconds', coalesce(round(avg(mx))::int, 0),
        'sessions',    count(*)
      ) from (
        select max(seconds) as mx
        from public.cf_events
        where type = 'page_time' and ts > since and seconds between 1 and 7200
        group by session, path
      ) g
    )
  );

  return res;
end;
$$;

grant execute on function public.cf_stats_full(integer) to authenticated;

-- =============================================================================
-- gata. Vechiul cf_stats() rămâne intact pentru orice; panoul nou folosește
-- cf_stats_full(). Nimic nu se șterge.
-- =============================================================================
