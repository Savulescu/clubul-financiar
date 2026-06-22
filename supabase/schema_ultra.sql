-- =============================================================================
-- schema_ultra.sql — Profilul Financiar al utilizatorului pentru suita ULTRA.
-- Stocare HIBRIDĂ: clientul scrie întâi în localStorage; dacă userul activează
-- sync-ul, oglindim aici (un singur rând per user, payload JSONB versionat).
-- RLS strict: fiecare user vede/scrie DOAR rândul lui.
-- Rulează în Supabase SQL editor. Idempotent.
-- =============================================================================

create table if not exists public.ultra_profile (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.ultra_profile enable row level security;

drop policy if exists "ultra_profile_select_own" on public.ultra_profile;
create policy "ultra_profile_select_own" on public.ultra_profile
  for select using (auth.uid() = user_id);

drop policy if exists "ultra_profile_insert_own" on public.ultra_profile;
create policy "ultra_profile_insert_own" on public.ultra_profile
  for insert with check (auth.uid() = user_id);

drop policy if exists "ultra_profile_update_own" on public.ultra_profile;
create policy "ultra_profile_update_own" on public.ultra_profile
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "ultra_profile_delete_own" on public.ultra_profile;
create policy "ultra_profile_delete_own" on public.ultra_profile
  for delete using (auth.uid() = user_id);

-- Snapshot-uri lunare de avere (pentru graficul "averea ta în timp" din Cockpit
-- și Raportul lunar). Refolosim tabelul existent `tool_logs` (tool='ultra-cockpit',
-- period='YYYY-MM', payload={avereNeta, venit, economii, scor}) — nu mai e nevoie
-- de tabel nou. Vezi cf-tool.js → CF.logEntry / CF.syncLog.
