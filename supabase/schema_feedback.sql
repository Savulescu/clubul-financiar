-- Tabel feedback de la utilizatori (toate într-un singur loc)
-- Rulează în Supabase: SQL Editor → paste → Run.

create table if not exists public.feedback (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  category text,
  message text not null,
  email text,
  page text,
  user_id uuid references auth.users(id) on delete set null
);

alter table public.feedback enable row level security;

-- Oricine (chiar nelogat) poate TRIMITE feedback
drop policy if exists "feedback insert" on public.feedback;
create policy "feedback insert" on public.feedback
  for insert to anon, authenticated with check (true);

-- DOAR adminul poate CITI toate feedback-urile
drop policy if exists "feedback admin read" on public.feedback;
create policy "feedback admin read" on public.feedback
  for select using ( lower(auth.jwt() ->> 'email') = 'clubulfinanciar@gmail.com' );
