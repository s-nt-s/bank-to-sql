from pathlib import Path
from typing import Union
import re
from datetime import date
from core.movimiento import Movimiento
from core.category import SubCategory
from . import Reader, IsNotForMeException
from core.filemanager import FM

re_sp = re.compile(r"\s+")

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


def find_account(txt: str):
    for prefix in ('DE37 5021 0900 70', 'ES42 1586 0001 44'):
        for m in re.findall(prefix.replace(" ", "")+r"(\d+)", txt):
            return f"{prefix} {m}"
    raise ValueError("Account not found in the document.")


def mk_re(*arr: str):
    res: list[str] = []
    for s in map(str.strip, arr):
        if s:
            res.append(r"\s*".join(map(re.escape, s.split())))
    r = r"|".join(res)
    return "("+r+")"


def load_trade_republic(file: Union[str, Path]):
    pdf: str = FM.load(file, physical=True)
    cnt = find_account(pdf)
    pdf = re.sub(r".*"+mk_re("TRANSACCIONES DE CUENTA"), "", pdf, flags=re.DOTALL)
    pdf = re.sub(mk_re("RESUMEN DEL BALANCE", "DISCLAIMER", "NOTAS SOBRE EL EXTRACTO DE CUENTA")+r".*", "", pdf, flags=re.DOTALL)

    pdf = re.sub(r"^\s*(Trade Republic Bank GmbH|Creado en \d+ \w+ \d+[\d,:]*|Página \d+ (de )?\d+)\s*$", "", pdf, flags=re.MULTILINE|re.DOTALL)
    pdf = re.sub(r"^\s*Creado en \d+ \w+ \d+[\d,: ]*\s*Página \d+ (de )?\d+\s*$", "", pdf, flags=re.MULTILINE|re.DOTALL)
    pdf = re.sub(mk_re('''
        Trade Republic Bank GmbH, Sucursal en España www.traderepublic.es Domicilio social: Trade Republic Bank GmbH                    Directores generales
        C/ Velazquez 50 - Planta 5                   NIF-IVA DE307510626 Brunnenstrasse 19-21, 10119 Berlín, Alemania                   Andreas Torner
        28001, Madrid, Madrid                                             Registrada en el Registro Mercantil del juzgado local de      Gernot Mittendorfer
        NIF: W0322893I                                                    Charlottenburg con el número HRB 244347 B, Alemania           Christian Hecker
                                                                                                                                        Thomas Pischke
    '''), "", pdf)
    pdf = re.sub(mk_re('''
        TRADE REPUBLIC BANK GMBH, SUCURSAL EN ESPAÑA C/ VELAZQUEZ 50 - PLANTA 5, MADRID 28001 - MADRID
    '''), "", pdf)
    pdf = re.sub(
        r"\n\s*" + mk_re("FECHA TIPO DESCRIPCIÓN ENTRADA DE DINERO SALIDA DE DINERO BALANCE") + r"\s*\n",
        "\n\n", pdf, flags=re.MULTILINE|re.DOTALL)
    pdf = re.sub(r"^\s*\n", "", pdf)
    pdf = re.sub(r"\n\s*$", "", pdf)
    pdf = re.sub(r"^\s+$", "", pdf, flags=re.MULTILINE)
    return re_sp.sub(r"", cnt), pdf


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
        lines = pdf.split("\n\n")
        head = re_sp.sub(" ", lines[0]).strip()
        lines = [ln for ln in lines if re_sp.sub(" ", ln).strip() != head]
        for row in lines:
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
    txt = " ".join(r[:12].rstrip() for r in row.split("\n"))
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
