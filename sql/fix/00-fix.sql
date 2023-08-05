UPDATE movimiento SET
    subcategoria=(
        select id from subcategoria where txt = 'Transferencias'
    )
where (
    subcategoria is null AND
    concepto like 'Transferencia emitida a %'
)
;

UPDATE movimiento SET
    subcategoria=(
        select id from subcategoria where txt = 'Deporte y gimnasio'
    )
where (
    UPPER(concepto) like '% CENTRO DEPORTIVO %' or
    UPPER(concepto) like '%AYTO % DEPORTES %'
) AND EXISTS (
    select id from subcategoria where txt = 'Deporte y gimnasio'
)
;

UPDATE movimiento SET
    subcategoria=(
        select id from subcategoria where txt = 'Teléfono, TV e internet'
    )
where (
    UPPER(concepto) like '%VODAFONE%'
) AND EXISTS (
    select id from subcategoria where txt = 'Teléfono, TV e internet'
);