-- Synchronisation en ligne du Tableau des quarts (Supabase, offre gratuite)
-- À exécuter une seule fois : Supabase > SQL Editor > New query > coller ce fichier > Run.
--
-- Principe : chaque élément (un équipier, un repas, un quart modifié, une denrée…)
-- est une ligne. Une ligne n'est remplacée que par une version plus récente
-- (dernière modification gagnante). Aucun accès direct à la table : tout passe
-- par deux fonctions qui exigent le code du bateau (au moins 12 caractères).

create table if not exists public.bord_records (
  boat    text    not null,
  k       text    not null,
  v       text,
  t       bigint  not null,
  deleted boolean not null default false,
  seq     bigserial,
  primary key (boat, k)
);
create index if not exists bord_records_boat_seq on public.bord_records (boat, seq);

alter table public.bord_records enable row level security;
revoke all on public.bord_records from anon, authenticated;

create or replace function public.bord_push(p_boat text, p_rows jsonb)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  r jsonb;
  n integer := 0;
begin
  if p_boat is null or length(p_boat) < 12 then
    raise exception 'code du bateau trop court (12 caracteres minimum)';
  end if;
  for r in select * from jsonb_array_elements(p_rows) loop
    insert into bord_records (boat, k, v, t, deleted)
    values (p_boat, r->>'k', r->>'v', (r->>'t')::bigint, coalesce((r->>'d')::boolean, false))
    on conflict (boat, k) do update
      set v = excluded.v,
          t = excluded.t,
          deleted = excluded.deleted,
          seq = nextval(pg_get_serial_sequence('public.bord_records', 'seq'))
      where excluded.t > bord_records.t;
    if found then n := n + 1; end if;
  end loop;
  return n;
end;
$$;

create or replace function public.bord_pull(p_boat text, p_since bigint)
returns table (k text, v text, t bigint, deleted boolean, seq bigint)
language sql
security definer
set search_path = public
as $$
  select r.k, r.v, r.t, r.deleted, r.seq
  from bord_records r
  where r.boat = p_boat and length(p_boat) >= 12 and r.seq > p_since
  order by r.seq
  limit 1000;
$$;

revoke all on function public.bord_push(text, jsonb) from public;
revoke all on function public.bord_pull(text, bigint) from public;
grant execute on function public.bord_push(text, jsonb) to anon;
grant execute on function public.bord_pull(text, bigint) to anon;
