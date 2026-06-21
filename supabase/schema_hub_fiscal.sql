-- ============================================================================
-- schema_hub_fiscal.sql — tabele pentru Hub Fiscal / unelte Pro
-- Rulează în Supabase: SQL Editor → New query → paste → Run.
-- (idempotent: poate fi rulat de mai multe ori)
-- ============================================================================

-- 1) ABONAMENTE (tier real, legat de Stripe ulterior) ------------------------
create table if not exists public.subscriptions (
  user_id uuid primary key references auth.users(id) on delete cascade,
  tier text not null default 'free' check (tier in ('free','premium','pro','ultra')),
  status text not null default 'active' check (status in ('active','canceled','past_due','trialing')),
  stripe_customer_id text,
  stripe_subscription_id text unique,
  current_period_end timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.subscriptions enable row level security;
drop policy if exists "own sub read" on public.subscriptions;
create policy "own sub read" on public.subscriptions for select using (auth.uid() = user_id);
-- INSERT/UPDATE se fac din webhook Stripe cu service_role (bypass RLS), nu din client.

-- 2) LOGARE UNELTE (recurență: venit/încasări/cheltuieli/etc. pe lună) --------
create table if not exists public.tool_logs (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  tool text not null,                      -- ex. 'radar-fiscal', 'plafon-tva'
  period text not null,                    -- 'YYYY-MM'
  payload jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  unique (user_id, tool, period)
);
alter table public.tool_logs enable row level security;
drop policy if exists "own logs all" on public.tool_logs;
create policy "own logs all" on public.tool_logs
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create index if not exists tool_logs_user_tool on public.tool_logs (user_id, tool);

-- 3) REMINDERE (citite de cronul lunar care trimite Telegram/email) ----------
create table if not exists public.reminders (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  tool text not null,
  kind text not null default 'monthly',    -- 'monthly' | 'deadline'
  note text,
  next_date date,                          -- pentru remindere de tip deadline
  channel text not null default 'telegram',-- 'telegram' | 'email'
  telegram_chat_id text,                   -- opțional, dacă userul și-a conectat Telegram
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (user_id, tool)
);
alter table public.reminders enable row level security;
drop policy if exists "own reminders all" on public.reminders;
create policy "own reminders all" on public.reminders
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- helper: updated_at automat
create or replace function public.touch_updated_at() returns trigger as $$
begin new.updated_at = now(); return new; end; $$ language plpgsql;
drop trigger if exists t_sub_touch on public.subscriptions;
create trigger t_sub_touch before update on public.subscriptions
  for each row execute function public.touch_updated_at();
drop trigger if exists t_log_touch on public.tool_logs;
create trigger t_log_touch before update on public.tool_logs
  for each row execute function public.touch_updated_at();
