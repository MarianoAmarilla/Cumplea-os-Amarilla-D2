-- Ejecutar DESPUÉS de supabase_setup.sql
-- Carga el listado inicial del equipo

insert into public.members (name, birthday, email) values
  ('Federico Alberto Cione',           '1984-07-14', ''),
  ('Lucas Craverou',                    '1991-05-06', ''),
  ('Carlos D''Alessandro',              '1988-04-22', ''),
  ('Fabricio Lioy',                     '1998-11-03', ''),
  ('Gabriela Soledad Marcos',           '1979-10-15', ''),
  ('Belen Mendes Diz Izuel',            '1993-09-20', ''),
  ('Ezequiel Miedvietzky',              '1983-03-03', ''),
  ('Gabriel Noriega',                   '1991-02-11', ''),
  ('Jorge Salleras',                    '1978-11-17', ''),
  ('Denise Salloum',                    '1991-07-30', ''),
  ('Ignacio Terán',                     '1996-05-14', ''),
  ('Karina Tizziani',                   '1975-11-19', ''),
  ('Mariano Valsecchi',                 '1993-04-23', ''),
  ('Jennifer Choi',                     '1993-01-10', ''),
  ('Jorhman Ricardo Escobar Escalona',  '1988-10-29', ''),
  ('Andrea Falco',                      '1984-05-04', ''),
  ('Ivan Pettino Ares',                 '2004-05-28', ''),
  ('David Alejandro Barrios Almandoz',  '1996-08-29', ''),
  ('Omar Dario Kischinovsky',           '1976-05-01', ''),
  ('Yohanny Carolina Yánez Colmenares', '1989-06-03', ''),
  ('Carolina Tripodoro',                '1997-08-21', '')
on conflict (email) do nothing;

-- Verificar
select name, to_char(birthday, 'DD/MM/YYYY') as cumpleaños
from public.members
order by to_char(birthday, 'MM-DD');
