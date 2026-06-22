-- =============================================================================
-- schema_newsletter.sql — abonați newsletter + preferințe + dezabonare
-- Rulează O DATĂ în Supabase: Dashboard → SQL Editor → New query → paste → Run.
-- =============================================================================

create extension if not exists pgcrypto;

-- ---- tabelul de abonați ----
create table if not exists public.newsletter_subscribers (
  id            uuid primary key default gen_random_uuid(),
  email         text not null unique,
  user_id       uuid references auth.users(id) on delete set null,  -- legat de cont dacă există
  tier_override text,                          -- NULL = ia tier-ul din subscriptions; altfel forțează
  subscribed    boolean not null default true, -- false = dezabonat
  unsub_token   text not null default encode(gen_random_bytes(16), 'hex'),
  source        text,                          -- de unde s-a înscris (ex. 'site', 'import')
  created_at    timestamptz not null default now()
);

alter table public.newsletter_subscribers enable row level security;

-- oricine se poate înscrie cu emailul lui (formularul de pe site, cu anon key)
drop policy if exists "newsletter self-signup" on public.newsletter_subscribers;
create policy "newsletter self-signup"
  on public.newsletter_subscribers for insert
  to anon, authenticated with check (true);
-- (fără policy de SELECT pentru anon ⇒ lista se citește DOAR server-side cu service key)

-- ---- dezabonare prin token (link din email) ----
create or replace function public.newsletter_unsubscribe(token text)
returns void language sql security definer as $$
  update public.newsletter_subscribers set subscribed = false where unsub_token = token;
$$;
grant execute on function public.newsletter_unsubscribe(text) to anon, authenticated;

-- ---- destinatarii unui newsletter, pe TIER EXACT (un singur email per user) ----
-- tier efectiv = tier_override, altfel abonamentul activ din subscriptions, altfel 'free'.
-- Trimiți newsletterul fiecărui tier doar celor cu acel tier:
--   newsletter_recipients('free')    → useri free + înscriși fără cont
--   newsletter_recipients('premium') → abonați Premium
--   newsletter_recipients('pro')     → abonați Pro
--   newsletter_recipients('ultra')   → abonați Ultra
create or replace function public.newsletter_recipients(want_tier text)
returns table(email text, unsub_token text, user_id uuid)
language sql security definer as $$
  select ns.email, ns.unsub_token, ns.user_id
  from public.newsletter_subscribers ns
  where ns.subscribed = true
    and coalesce(
          ns.tier_override,
          (select s.tier from public.subscriptions s
            where s.user_id = ns.user_id and s.status = 'active'
              and (s.current_period_end is null or s.current_period_end > now())
            order by 1 limit 1),
          'free'
        ) = want_tier;
$$;
grant execute on function public.newsletter_recipients(text) to service_role;

-- ---- OPȚIONAL: pre-populează abonații din userii existenți (rulează o dată) ----
-- insert into public.newsletter_subscribers (email, user_id, source)
-- select u.email, u.id, 'import'
-- from auth.users u
-- on conflict (email) do nothing;
