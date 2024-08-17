with M as (
	select m.*, s.txt sub from movimiento m join subcategoria s on m.subcategoria=s.id where importe!=0
),
E as (
	select * from M where importe>0
),
S as (
	select * from M where importe<0
),
T as (
	select 
		E.importe,
		S.id salida,
		E.id entrada,
		S.fecha s_fecha,
		julianday(E.fecha) - julianday(S.fecha) AS dias,
		S.sub s_sub,
		E.sub e_sub,
		S.concepto s_concepto,
		E.concepto e_concepto
	from E join S on E.importe = -S.importe and E.fecha>=S.fecha
	where S.cuenta!=E.cuenta and (julianday(E.fecha) - julianday(S.fecha))<8
),
aux1 as (
	select salida, entrada, min(dias) dias from T group by salida, entrada
),
aux2 as (
	select min(salida) salida, entrada, dias from aux1 group by entrada, dias
),
aux3 as (
	select salida, min(entrada) entrada, dias from aux2 group by salida, dias
)
select * from T where (salida, entrada, dias) in (
	select salida, entrada, dias from aux3
)


