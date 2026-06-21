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

-- Evidențiere (pin) + ștergere/actualizare doar de admin
alter table public.feedback add column if not exists pinned boolean default false;
grant update, delete on public.feedback to authenticated;
drop policy if exists "fb admin update" on public.feedback;
create policy "fb admin update" on public.feedback for update to authenticated
  using ( lower(auth.jwt() ->> 'email') = 'clubulfinanciar@gmail.com' )
  with check ( lower(auth.jwt() ->> 'email') = 'clubulfinanciar@gmail.com' );
drop policy if exists "fb admin delete" on public.feedback;
create policy "fb admin delete" on public.feedback for delete to authenticated
  using ( lower(auth.jwt() ->> 'email') = 'clubulfinanciar@gmail.com' );
notify pgrst, 'reload schema';
