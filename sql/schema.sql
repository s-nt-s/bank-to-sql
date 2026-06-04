CREATE TABLE cuenta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL,
  carpeta TEXT NOT NULL
);
CREATE TABLE categoria (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL UNIQUE
);
CREATE TABLE subcategoria (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL UNIQUE,
  categoria INTEGER NOT NULL DEFAULT -1,
  FOREIGN KEY(categoria) REFERENCES categoria(id)
);

CREATE TABLE movimiento (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cuenta INTEGER,
  fecha DATE,
  subcategoria INTEGER NOT NULL DEFAULT -1,
  concepto TEXT,
  importe REAL,
  FOREIGN KEY(cuenta) REFERENCES cuenta(id),
  FOREIGN KEY(subcategoria) REFERENCES subcategoria(id)
);

insert into categoria (id, txt) values
(0, 'Saldo inicial');
insert into subcategoria (id, txt, categoria) values
(0, 'Saldo inicial', 0);

insert into categoria (id, txt) values
(-1, 'Sin categoria');
insert into subcategoria (id, txt, categoria) values
(-1, 'Sin subcategoria', -1);

insert into categoria (id, txt) values
(-2, 'Transacción entre cuentas');
insert into subcategoria (id, txt, categoria) values
(-2, 'Transacción entre cuentas', -2);

create VIEW MOV AS
select
  m.id,
  m.fecha,
  c.txt categoria,
  s.txt subcategoria,
  m.concepto,
  m.importe
from
  movimiento m 
  join subcategoria s on m.subcategoria=s.id
  join categoria c on s.categoria=c.id
order by
  m.fecha desc
;

create VIEW MOV_DIARIO AS
select
  fecha,
  categoria,
  subcategoria,
  concepto,
  sum(importe) importe
from (
  select
    fecha,
    CASE
      WHEN importe>0 and subcategoria in (
        'Abono de intereses',
        'Nómina o Pensión',
        'Alquiler'
      ) THEN 'Rentas'
      ELSE categoria
    END categoria,
    CASE
      WHEN importe>0 and subcategoria in (
        'Abono de intereses',
        'Nómina o Pensión',
        'Alquiler'
      ) THEN 'Rentas'
      ELSE subcategoria
    END subcategoria,
    CASE
      WHEN importe>0 and subcategoria in (
        'Abono de intereses',
        'Nómina o Pensión',
        'Alquiler'
      ) THEN 'Rentas'
      WHEN subcategoria = 'Transacción entre cuentas' THEN subcategoria
      ELSE concepto
    END concepto,
    importe
  from
    MOV
) aux
group by
  fecha,
  categoria,
  subcategoria,
  concepto
having
  sum(importe) != 0
order by
  fecha desc
;

create VIEW RESUMEN_DIARIO as
select
  fecha,
  subcategoria,
  concepto,
  sum(importe) importe
from
  movimiento
group by
  fecha,
  subcategoria,
  concepto
;

create VIEW RESUMEN_MENSUAL as
select
  substr(fecha, 1, 7) mes,
  subcategoria,
  concepto,
  sum(importe) importe
from
  movimiento
group by
  substr(fecha, 1, 7),
  subcategoria,
  concepto
;

create VIEW RESUMEN_ANUAL as
select
  substr(fecha, 1, 4) anio,
  subcategoria,
  concepto,
  sum(importe) importe
from
  movimiento
group by
  substr(fecha, 1, 7),
  subcategoria,
  concepto
;