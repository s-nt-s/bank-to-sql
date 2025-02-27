import re
from core.movimiento import Movimiento
from core.excel import Excel
from core.category import SubCategory
from . import Reader, IsNotForMeException
from core.filemanager import FM


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


class MyInvestorReader(Reader):
    def read(self):
        ws: Excel = FM.load(self.path)
        cnt = 'ES38 1544 7889 76 ' + ws.get_text(3, 4)
        arr = []
        for i in range(10, ws.nrows):
            concepto = ws.get_text(i, 3)
            m = Movimiento(
                cuenta=cnt,
                fecha=ws.get_date(i, 2),
                subcategoria=_get_subcat(concepto),
                concepto=concepto,
                importe=ws.get_number(i, 5),
                saldo=ws.get_number(i, 6)
            )
            arr.append(m)
        yield from arr

    def _check_file(self):
        if self.path.suffix != ".xlsx":
            raise IsNotForMeException(f"{self.path}")
        ws: Excel = FM.load(self.path)
        cnt = ws.get_word(3, 4)
        if cnt is None:
            raise IsNotForMeException(f"{self.path}")
        return cnt.isdigit()
