from core.movimiento import Movimiento
from core.excel import Excel
from . import Reader, IsNotForMeException
from core.category import SubCategory
import re
from core.filemanager import FM


def _get_subcat(c: str, s: str, concepto: str):
    if (c, s) == (None, None):
        return SubCategory.SIN_SUBCATEGORIA
    if s in ("Farmacia", "Farmacia, herbolario y nutrición"):
        return SubCategory.FARMACIA_HERBOLARIO_NUTRICION
    if s in ("Taxis", "Taxis y Carsharing"):
        return SubCategory.TAXI_CARSHARING
    if s == "Educación":
        return SubCategory.EDUCACION
    if s == "Otros ingresos":
        return SubCategory.OTROS_INGRESOS
    if s == "Hogar":
        return SubCategory.HOGAR_OTROS
    if s == "Tren, avión, transporte":
        return SubCategory.BILLETES_VIAJE
    if s in ("Transacción entre cuentas de ahorro", 'Traspaso entre cuentas'):
        return SubCategory.TRANSACCION_CUENTAS
    if s == "Abono de intereses":
        return SubCategory.ABONO_INTERESES
    if s == "Pagos impuestos":
        return SubCategory.IMPUESTOS_OTROS
    if s == "Belleza y perfumería":
        return SubCategory.BELLEZA_PELUQUERIA_PERFUMERIA
    if s == "Otras inversiones":
        return SubCategory.OTRAS_INVERSIONES
    if s == "Libros, música y videojuegos":
        return SubCategory.LIBROS_MUSICA_JUEGOS
    if s == 'Dentista, médico':
        return SubCategory.DENTISTA_MEDICO
    if s in ('Pago de impuestos', 'Impuestos hogar'):
        return SubCategory.IMPUESTOS_OTROS
    if s == 'Alquiler vivienda':
        return SubCategory.ALQUILER
    if s == 'Deporte y gimnasio':
        return SubCategory.DEPORTE_GIMNASIO
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
        ini, _, cnt = self.__get_account_index(ws)
        arr = []
        for i in range(ini+5, ws.nrows):
            fecha = None
            try:
                fecha = ws.get_date(i, 0)
            except (ValueError, TypeError):
                continue
            if fecha is None:
                continue
            categoria = ws.get_text(i, 1)
            subcategoria = ws.get_text(i, 2)
            concepto = ws.get_text(i, 3)
            importe = ws.get_number(i, 6)
            if importe is None:
                importe = ws.get_number(i, 5)
            m = Movimiento(
                cuenta=cnt,
                fecha=fecha,
                subcategoria=_get_subcat(categoria, subcategoria, concepto),
                concepto=concepto,
                importe=importe,
                saldo=ws.get_number(i, 7)
            )
            arr.append(m)
        yield from reversed(arr)

    def __get_account_index(self, ws: Excel):
        for row, cel in (
            (0, 3),
            (1, 3),
        ):
            cnt = self.__get_account(ws, row, cel)
            if cnt is not None:
                return row, cel, cnt
        return None

    def __get_account(self, ws: Excel, row: int, cel: int):
        cnt = ws.get_word(row, cel)
        if not isinstance(cnt, str):
            return None
        if re.match(r"ES\d+", cnt):
            return cnt
        if not cnt.isdigit() or len(cnt) != 20:
            return None
        txt = FM.safe_load(self.path.parent / "cuenta.txt")
        if not isinstance(txt, str):
            return None
        txt = txt.strip()
        if txt.endswith(cnt):
            return txt

    def _check_file(self):
        if self.path.suffix != ".xls":
            raise IsNotForMeException(f"{self.path}")
        ws: Excel = FM.load(self.path)
        cntI = self.__get_account_index(ws)
        if cntI is None:
            raise IsNotForMeException(f"{self.path}")
