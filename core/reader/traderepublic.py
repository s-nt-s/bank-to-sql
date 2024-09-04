from pathlib import Path
from typing import Union
import pdftotext
import re
from datetime import date
from core.movimiento import Movimiento
from core.category import SubCategory
from . import Reader, IsNotForMeException
from core.filemanager import FM


CNT_PREFIX = 'DE37 5021 0900 70 '
MES = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic")
re_sp = re.compile(r"\s+")


def _to_num(s: str):
    s = re.sub(r"\s*€$", "", s)
    if "," in s:
        s = s.replace(".", "")
        s = s.replace(",", ".")
    f = float(s)
    i = int(f)
    return i if i == f else f


def load_trade_republic(file: Union[str, Path]):
    pdf: str = FM.load(file, physical=True)
    cnt = CNT_PREFIX + re.findall(CNT_PREFIX.replace(" ", "")+r"(\d+)", pdf)[0]
    pdf = pdf.split("TRANSACCIONES DE CUENTA")[1]
    pdf = re.sub(r"^\s*(Trade Republic Bank GmbH|Página [\d ]+|Creado en \d+ \w+ \d+)\s*$", "", pdf, flags=re.MULTILINE)
    pdf = pdf.split("DISCLAIMER")[0]
    pdf = re.sub(r"^\s*\n", "", pdf)
    pdf = re.sub(r"\n\s*$", "", pdf)
    pdf = re.sub(r"^\s+$", "", pdf, flags=re.MULTILINE)
    return cnt, pdf


def _get_subcat(row: str):
    if "Your interest payment" in row:
        return SubCategory.ABONO_INTERESES
    if "Ingreso aceptado" in row:
        return SubCategory.TRANSFERENCIA_BANCARIA
    if "Reembolso por tu regalo" in row:
        return SubCategory.ABONO_INTERESES
    if "Buy trade" in row:
        return SubCategory.OTRAS_INVERSIONES
    return SubCategory.SIN_SUBCATEGORIA


class TradeRepublicReader(Reader):
    def read(self):
        cnt, pdf = load_trade_republic(self.path)
        arr: list[Movimiento] = []
        for row in pdf.split("\n\n")[1:]:
            concepto = get_concepto(row)
            imp, saldo = get_importe_saldo(row)
            if (arr and arr[-1].saldo > saldo):
                imp = -imp
            arr.append(Movimiento(
                cuenta=cnt,
                fecha=get_date(row),
                concepto=concepto,
                subcategoria=_get_subcat(row),
                importe=imp,
                saldo=saldo
            ))
        yield from arr

    def _check_file(self):
        if self.path.suffix != ".pdf":
            raise IsNotForMeException(f"{self.path}")
        try:
            cnt, pdf = load_trade_republic(self.path)
        except Exception:
            raise IsNotForMeException(f"{self.path}")


def get_date(row: str):
    txt = " ".join(r[:11] for r in row.split("\n"))
    m = re.search(r"(\d{2})\s*("+("|".join(MES))+")\s*(\d{4})", txt)
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
