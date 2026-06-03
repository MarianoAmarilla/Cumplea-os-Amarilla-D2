-- Ejecutar en Supabase > SQL Editor

-- Tabla única para todos los miembros
create table if not exists public.members (
  id         serial primary key,
  name       text not null,
  email      text not null unique,
  birthday   date not null,
  created_at timestamptz default now()
);

-- Sin RLS restrictivo: cualquiera puede leer e insertar (no requiere login)
alter table public.members enable row level security;

create policy "Lectura pública"
  on public.members for select
  using (true);

create policy "Inserción pública"
  on public.members for insert
  with check (true);

create policy "Actualización por email"
  on public.members for update
  using (true);
