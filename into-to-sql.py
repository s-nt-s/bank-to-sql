#!/usr/bin/env python3

import argparse
import re
from datetime import datetime, timedelta, date
from os import chdir, remove
from os.path import abspath, dirname, isdir, isfile, exists, expanduser
from pathlib import Path
from core.movimiento import Movimiento
import sqlite3
import sys
from core.dbing import DBIng

import xlrd

abspath = abspath(__file__)
dname = dirname(abspath)
chdir(dname)

parser = argparse.ArgumentParser(description='Genera base de datos sqlite a partir de excel de movimientos de ING')
parser.add_argument("--xls", help="Fichero de movimientos o carpeta donde buscarlos", required=True)
parser.add_argument("--ini", type=int, help="Año de inicio", required=True)
parser.add_argument("--out", help="Base de datos de salida", required=True)

re_year = re.compile(r"^_?((20|19)\d\d).*")
re_sp = re.compile(r"\s+")

CUENTAS = {}
MOVIMIENTOS = set()
INDEX = {}

def safe_sum(*arr):
    dec = max(map(lambda x:len(str(float(x)).split(".")[-1]), arr))
    mul = pow(10, dec+1)
    arr = tuple(map(lambda x:x*mul, arr))
    return sum(arr)/mul

def get_sheet(f, index=0):
    wb = xlrd.open_workbook(f)
    ws = wb.sheet_by_index(index)
    return wb, ws

def get_val(ws, r, c):
     v = ws.cell(r, c)
     return v.value

def get_movmientos(f):
    wb, ws = get_sheet(f)
    cnt = ws.cell(1, 3)
    cnt = re_sp.sub(" ", cnt.value).strip()
    arr = []
    for i in range(6, ws.nrows):
        values = ws.row_values(i)
        m = Movimiento(cnt, wb, values)
        arr.append(m)
    yield from reversed(arr)


def parse_file(path):
    for i, m in enumerate(get_movmientos(path)):
        MOVIMIENTOS.add(m)
        key = m.get_key()
        if key not in INDEX or INDEX[key][0] > path.name:
            INDEX[key] = (path.name, i)

def iter_path(source):
    if isfile(source):
        yield Path(source)
    else:
        paths = []
        for path in Path(source).rglob('*.xls'):
            m = re_year.match(path.name)
            if not m:
                continue
            year = int(m.group(1))
            if year < args.ini:
                continue
            paths.append((year, path))
        for _, path in sorted(paths):
            yield path

if __name__ == "__main__":
    args = parser.parse_args()
    if not exists(args.xls):
        sys.exit("No existe --xls %s" % args.xls)
    if (False, False) == (isfile(args.xls), isdir(args.xls)):
        sys.exit("No es un fichero ni un directorio --xls %s" % args.xls)
    for path in iter_path(args.xls):
        print(path)
        parse_file(path)
    MOVIMIENTOS=sorted(MOVIMIENTOS, key=lambda m: (m.fecha, INDEX[m.get_key()]))
    if len(MOVIMIENTOS) == 0:
        sys.exit("No hay movimientos")

    cuentas = {}
    for m in MOVIMIENTOS:
        if m.cuenta not in cuentas:
            cuentas[m.cuenta] = m
    saldo = 0
    for c, m in cuentas.items():
        saldo = safe_sum(saldo, m.saldo, -m.importe)

    last={}
    with DBIng(args.out, reload=True) as db:
        for m in MOVIMIENTOS:
            last[m.cuenta] = m.saldo
            saldo = safe_sum(saldo, m.importe)
            if not m.is_interno:
                m.saldo = saldo
                db.set_movimiento(m)
