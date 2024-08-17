from core.movimiento import Movimiento
from core.excel import Excel
from . import Reader, IsNotForMeException
from core.category import SubCategory
import re
from core.filemanager import FM


def _get_subcat(c: str, s: str, concepto: str):
    if (c, s) == (None, None):
        return SubCategory.SIN_SUBCATEGORIA
    if s == "Farmacia":
        return SubCategory.FARMACIA_HERBOLARIO_NUTRICION
    if s == "Taxis":
        return SubCategory.TAXI_CARSHARING
    if s == "Educación":
        return SubCategory.EDUCACION
    if s == "Otros ingresos":
        return SubCategory.OTROS_INGRESOS
    if s == "Hogar":
        return SubCategory.HOGAR_OTROS
    if s == "Tren, avión, transporte":
        return SubCategory.BILLETES_VIAJE
    if s == "Transacción entre cuentas de ahorro":
        return SubCategory.TRANSACCION_CUENTAS
    if s == "Abono de intereses":
        return SubCategory.ABONO_INTERESES
    if s == "Pagos impuestos":
        return SubCategory.IMPUESTOS_OTROS
    if concepto in ('Traspaso emitido Cuenta Nómina', 'Traspaso recibido Cuenta Nómina'):
        return SubCategory.TRANSACCION_CUENTAS
    sub = SubCategory.find(s)
    cat = sub.parent()
    if c not in (None, "Movimiento sin categoría") and str(cat) != c:
        raise ValueError(f"Category mismatch: {c} != {cat}, for {s}")
    return sub


class IngReader(Reader):
    def read(self):
        ws: Excel = FM.load(self.path)
        cnt = ws.get_text(1, 3)
        arr = []
        for i in range(6, ws.nrows):
            categoria = ws.get_text(i, 1)
            subcategoria = ws.get_text(i, 2)
            concepto = ws.get_text(i, 3)
            m = Movimiento(
                cuenta=cnt,
                fecha=ws.get_date(i, 0),
                subcategoria=_get_subcat(categoria, subcategoria, concepto),
                concepto=concepto,
                importe=ws.get_number(i, 6),
                saldo=ws.get_number(i, 7)
            )
            arr.append(m)
        yield from reversed(arr)

    def _check_file(self):
        if self.path.suffix != ".xls":
            raise IsNotForMeException(f"{self.path}")
        ws: Excel = FM.load(self.path)
        cnt = ws.get_word(1, 3)
        if cnt is None:
            raise IsNotForMeException(f"{self.path}")
        if re.match(r"ES\d+", cnt) is None:
            raise IsNotForMeException(f"{self.path}")
