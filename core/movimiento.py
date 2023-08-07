from datetime import datetime, date
import xlrd
import re
from functools import cache
from xlrd import Book
from xlrd.sheet import Sheet
from typing import NamedTuple
from pathlib import Path

re_sp = re.compile(r"\s+")
re_deporte = re.compile(r"\b(CENTRO DEPORTIVO|AYTO .* DEPORTES)\b", re.IGNORECASE)
re_telefono = re.compile(r"\bVODAFONE\b", re.IGNORECASE)


def get_date(book, s):
    if s:
        d = datetime(*xlrd.xldate_as_tuple(s, book.datemode))
        return d.date()


def get_text(s):
    if s is None:
        return None
    s = re_sp.sub(" ", s)
    s = s.strip()
    if len(s) == 0:
        return None
    return s


def get_subcat(s):
    s = get_text(s)
    if s == "Farmacia":
        return "Farmacia, herbolario y nutrición"
    if s == "Taxis":
        return "Taxi y Carsharing"
    if s == "Educación":
        return "Educación, salud y deporte"
    if s == "Otros ingresos":
        return "Otros ingresos (otros)"
    if s == "Hogar":
        return "Hogar (otros)"
    if s == "Tren, avión, transporte":
        return "Billetes de viaje"
    return s


class Movimiento(NamedTuple):
    cuenta: str
    fecha: date
    categoria: str
    subcategoria: str
    concepto: str
    importe: float
    saldo: float
    interno: bool = False

    @staticmethod
    def reader(file: str | Path):
        wb: Book = xlrd.open_workbook(file)
        ws: Sheet = wb.sheet_by_index(0)
        cnt = ws.cell(1, 3).value
        cnt = re_sp.sub(" ", cnt).strip()
        arr = []
        for i in range(6, ws.nrows):
            row: list = ws.row_values(i)
            m = Movimiento(
                cuenta=cnt,
                fecha=get_date(wb, row[0]),
                categoria=get_text(row[1]),
                subcategoria=get_subcat(row[2]),
                concepto=get_text(row[3]),
                importe=row[6],
                saldo=row[7]
            )
            arr.append(m)
        yield from reversed(arr)

    @cache
    def maybe_interno(self):
        if self.subcategoria == "Transacción entre cuentas de ahorro":
            return True
        if self.concepto in ("Traspaso recibido Cuenta Nómina",):
            return True
        if self.concepto in ("Traspaso emitido Cuenta Nómina",):
            return True
        return False

    def is_traspaso(self, m: "Movimiento"):
        if not self.maybe_interno:
            return False
        if not m.maybe_interno:
            return False
        if self.cuenta == m.cuenta:
            return False
        if self.importe != -m.importe:
            return False
        if self.fecha != m.fecha:
            return False
        return True

    def replace(self, **kwargs):
        return Movimiento(**{
            **self._asdict(),
            **kwargs
        })
