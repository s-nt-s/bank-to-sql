from datetime import datetime, timedelta, date
import xlrd
import re
from functools import lru_cache

re_sp = re.compile(r"\s+")


def get_date(book, s):
    if s:
        d = datetime(*xlrd.xldate_as_tuple(s, book.datemode))
        return d.date()

def get_text(s):
    if s is None:
        return None
    s = re_sp.sub(" ", s)
    s = s.strip()
    if len(s)==0:
        return None
    return s

class Movimiento:
    def __init__(self, cuenta, book, row):
        super().__init__()
        self.cuenta = cuenta
        self.fecha = get_date(book, row[0])
        self.categoria = get_text(row[1])
        self.subcategoria = get_text(row[2])
        self.concepto = get_text(row[3])
        self.importe = row[6]
        self.saldo = row[7]

    def get_key(self):
        k = sorted(self.__dict__.items(), key=lambda x:x[0])
        return tuple(k)

    def __eq__(self, o):
        return self.get_key() == o.get_key()

    def __hash__(self):
        return hash(self.get_key())

    @property
    @lru_cache(maxsize=None)
    def is_interno(self):
        c = self.concepto

        if self.subcategoria == "Transacción entre cuentas de ahorro":
            return True
        if c in ("Traspaso recibido Cuenta Nómina",):
            return True
        if c in ("Traspaso emitido Cuenta Nómina",):
            return True

        return False
