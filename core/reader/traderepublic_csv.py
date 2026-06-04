from pathlib import Path
from typing import Union
import re
from datetime import date
from core.movimiento import Movimiento
from core.category import SubCategory
from . import Reader, IsNotForMeException
from core.filemanager import FM
from typing import Tuple, Dict

re_sp = re.compile(r"\s+")

MES = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic")
re_sp = re.compile(r"\s+")

HEAD = (
    "datetime",
    "date",
    "account_type",
    "category",
    "type",
    "asset_class",
    "name",
    "symbol",
    "shares",
    "price",
    "amount",
    "fee",
    "tax",
    "currency",
    "original_amount",
    "original_currency",
    "fx_rate",
    "description",
    "transaction_id",
    "counterparty_name",
    "counterparty_iban",
    "payment_reference",
    "mcc_code"
)


def _to_num(s: str):
    s = re.sub(r"\s*€$", "", s)
    if "," in s:
        s = s.replace(".", "")
        s = s.replace(",", ".")
    f = float(s)
    i = int(f)
    return i if i == f else f


def _get_subcat(row: str):
    if "Interest payment for payout collection" in row:
        return SubCategory.ABONO_INTERESES
    if "Reembolso por tu regalo" in row:
        return SubCategory.ABONO_INTERESES
    if "Your interest payment" in row:
        return SubCategory.ABONO_INTERESES
    if "Ingreso aceptado" in row:
        return SubCategory.TRANSFERENCIA_BANCARIA
    if "Buy trade" in row:
        return SubCategory.OTRAS_INVERSIONES
    return SubCategory.SIN_SUBCATEGORIA


def to_date(s: str):
    if s is None or isinstance(s, date):
        return s
    if not isinstance(s, str):
        raise ValueError("El argumento ha de ser un str")
    return date(*map(int, s.split("-")))


def to_num(*args: str):
    val = 0
    for s in args:
        if s in (None, ''):
            continue
        if isinstance(s, str):
            s = float(s)
        if not isinstance(s, (int, float, int)):
            raise ValueError(s)
        val = val + s
    i = int(val)
    return i if val == i else val


class TradeRepublicReader(Reader):
    def read(self):
        rows: tuple[dict] = FM.load(self.path, delimiter=',')
        cnt = FM.load(self.path.parent / "cuenta.txt")
        cnt = re_sp.sub(r"", cnt)
        arr = []
        for r in rows:
            concepto = r['description']
            m = Movimiento(
                cuenta=cnt,
                fecha=to_date(r['date']),
                subcategoria=_get_subcat(concepto),
                concepto=concepto,
                importe=to_num(r['amount'], r['fee'], r['tax']),
                saldo=None,
                index=len(arr)
            )
            arr.append(m)
        yield from arr

    def _check_file(self):
        if self.path.suffix != ".csv":
            raise IsNotForMeException(f"{self.path}")
        csv = FM.load(self.path, delimiter=',')
        if not isinstance(csv, tuple) or len(csv) == 0:
            raise IsNotForMeException(f"{self.path}")
        head = tuple(csv[0].keys())
        if head != HEAD:
            raise IsNotForMeException(f"{self.path}")
        return True


def get_date(row: str):
    txt = " ".join(r[:11].rstrip() for r in row.split("\n"))
    m = re.search(r"(\d{2})\s*("+("|".join(MES))+r")\s*(\d{4})", txt)
    if m is None:
        raise ValueError(f"Date not found in:\n{row}")
    d, m, y = m.groups()
    return date(int(y), MES.index(m)+1, int(d))


def get_importe_saldo(row: str):
    arr = tuple(map(_to_num, re.findall(r"(\d[\d.,]+) €", row)))
    if len(arr) != 2:
        raise ValueError(f"importe/saldo not found in {row}")
    return arr


def get_concepto(row: str):
    txt = " ".join(r[11:] for r in row.split("\n"))
    txt = re.sub(r"(\d[\d.,]+) €", "", txt)
    txt = re_sp.sub(" ", txt)
    txt = txt.strip()
    if len(txt) == 0:
        return None
    return txt
