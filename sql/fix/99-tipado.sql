insert into tipo (id, txt) values
(1, 'IRPF'),
(2, 'IBI'),
(3, 'Devolución')
;

insert into tipado (movimiento, tipo)
select
    id, 3
from
    movimiento
where
    lower(concepto) like 'devolución %' or
    lower(concepto) like 'devolucion %'
;