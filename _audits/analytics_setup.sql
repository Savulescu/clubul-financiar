-- ============================================================
-- Clubul Financiar — statistici vizitatori (rulează o dată în Supabase → SQL Editor → Run)
-- ============================================================

-- 1) tabelul de pageview-uri
create table if not exists public.page_views (
  id bigint generated always as identity primary key,
  ts timestamptz not null default now(),
  path text,
  visitor text,
  referrer text
);
create index if not exists page_views_ts_idx on public.page_views (ts);

-- 2) RLS: oricine poate INSERA un pageview, dar NIMENI nu poate citi rândurile direct
alter table public.page_views enable row level security;

drop policy if exists "cf insert pageviews" on public.page_views;
create policy "cf insert pageviews" on public.page_views
  for insert to anon, authenticated with check (true);

-- 3) funcție agregată — întoarce numerele pe intervale, DOAR pentru adminul tău
create or replace function public.cf_stats()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  email text := (auth.jwt() ->> 'email');
  res jsonb;
begin
  if email is null or lower(email) <> 'clubulfinanciar@gmail.com' then
    raise exception 'forbidden';
  end if;
  select jsonb_build_object(
    'h24',  jsonb_build_object('views', count(*) filter (where ts > now() - interval '24 hours'),
                               'visitors', count(distinct visitor) filter (where ts > now() - interval '24 hours')),
    'd7',   jsonb_build_object('views', count(*) filter (where ts > now() - interval '7 days'),
                               'visitors', count(distinct visitor) filter (where ts > now() - interval '7 days')),
    'd30',  jsonb_build_object('views', count(*) filter (where ts > now() - interval '30 days'),
                               'visitors', count(distinct visitor) filter (where ts > now() - interval '30 days')),
    'd90',  jsonb_build_object('views', count(*) filter (where ts > now() - interval '90 days'),
                               'visitors', count(distinct visitor) filter (where ts > now() - interval '90 days')),
    'd180', jsonb_build_object('views', count(*) filter (where ts > now() - interval '180 days'),
                               'visitors', count(distinct visitor) filter (where ts > now() - interval '180 days')),
    'd365', jsonb_build_object('views', count(*) filter (where ts > now() - interval '365 days'),
                               'visitors', count(distinct visitor) filter (where ts > now() - interval '365 days')),
    'total', jsonb_build_object('views', count(*), 'visitors', count(distinct visitor))
  ) into res from public.page_views;
  return res;
end;
$$;

grant execute on function public.cf_stats() to authenticated;
