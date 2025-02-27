import re
from core.movimiento import Movimiento
from core.category import SubCategory
from core.filemanager import FM
from typing import Union, Dict, Tuple
from . import Reader, IsNotForMeException
from datetime import date

CSV = Tuple[Dict[str, Union[str, int, float]]]

re_sp = re.compile(r"\s+")


def is_interes(s: str):
    if not isinstance(s, str):
        return False
    if re.search(r"PROMOCION AMIGO", s):
        return True
    return re.match(r"PERIODO [\d/ ]+", s) is not None


def _get_subcat(c: str):
    if is_interes(c):
        return SubCategory.ABONO_INTERESES
    if c == "ALIMENTACION":
        return SubCategory.SUPERMERCADOS_ALIMENTACION
    return SubCategory.SIN_SUBCATEGORIA


def to_date(s: str):
    if s is None or isinstance(s, date):
        return s
    if not isinstance(s, str):
        raise ValueError("El argumento ha de ser un str")
    d, m, y = map(int, s.split("/"))
    return date(y, m, d)


def to_num(s: str):
    if s is None or isinstance(s, (int, float, int)):
        return s
    if not isinstance(s, str):
        raise ValueError("El argumento ha de ser un str")
    f = float(s.replace('.', '').replace(',', '.'))
    i = int(f)
    return i if f==i else f


class MyInvestorReader(Reader):
    def read(self):
        rows: CSV = FM.load(self.path, delimiter=';')
        cnt = 'ES38 1544 7889 76 ' + FM.load(self.path.parent / "cuenta.txt")
        cnt = re_sp.sub(r"", cnt)
        arr = []
        for r in rows:
            concepto = r['Concepto']
            m = Movimiento(
                cuenta=cnt,
                fecha=to_date(r['Fecha de valor']),
                subcategoria=_get_subcat(concepto),
                concepto=concepto,
                importe=to_num(r['Importe']),
                saldo=None
            )
            arr.append(m)
        yield from arr

    def _check_file(self):
        if self.path.suffix != ".csv":
            raise IsNotForMeException(f"{self.path}")
        csv: CSV = FM.load(self.path, delimiter=';')
        if not isinstance(csv, tuple) or len(csv) == 0:
            raise IsNotForMeException(f"{self.path}")
        head = tuple(csv[0].keys())
        if ";".join(head) != 'Fecha de operación;Fecha de valor;Concepto;Importe;Divisa':
            raise IsNotForMeException(f"{self.path}")
        return True
