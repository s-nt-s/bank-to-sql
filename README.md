# ing-to-sql

Transforma los movimientos de varios bancos a una [base de datos sqlite](sql/schema.sql):

![Diagrama de la base de datos](sql/diagram.png)

Por ahora soporta:

* [ING](https://ing.ingdirect.es) (xls)
* [MyInvestor](https://app.myinvestor.es) (xlsx)
* [traderepublic](https://traderepublic.com/) (pdf)

## Requisitos

Tener descargados los movimientos en ficheros cuyo nombre
empiece por `YYYYY` o `_YYYY` donde `YYYY` es el año al que se refieren.

En caso de que un año este troceado en varios ficheros, los nombres
de dichos archivos deben coincidir con el orden cronológico,
por ejemplo `2010a.xls` contendrá movimientos anteriores a `2010b.xls`.

No importa si dos Excel se solapan (por ejemplo, que `2010a.xls` vaya
de enero al 30 de junio y `2010b.xls` del 1 de junio a diciembre), ya
que los movimientos duplicados se descartan.
