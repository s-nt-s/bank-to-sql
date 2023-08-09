#!/usr/bin/env python3

import argparse
import re
from os.path import dirname, isdir, isfile, exists, realpath, join
from pathlib import Path
from core.movimiento import Movimiento
import sys
from core.dbing import DBIng
from core.movimientos import Movimientos

re_year = re.compile(r"^_?((20|19)\d\d).*")
re_sp = re.compile(r"\s+")

CUENTAS = {}
MOVIMIENTOS: set[Movimiento] = set()
INDEX = {}


def safe_sum(*arr):
    dec = max(map(lambda x:len(str(float(x)).split(".")[-1]), arr))
    mul = pow(10, dec+1)
    arr = tuple(map(lambda x:x*mul, arr))
    return sum(arr)/mul


def parse_file(path: Path):
    for i, m in enumerate(Movimiento.reader(path)):
        MOVIMIENTOS.add(m)
        if m not in INDEX or INDEX[m][0] > path.name:
            INDEX[m] = (path.name, i)


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
    parser = argparse.ArgumentParser(description='Genera base de datos sqlite a partir de excel de movimientos de ING')
    parser.add_argument("--xls", help="Fichero de movimientos o carpeta donde buscarlos", required=True)
    parser.add_argument("--ini", type=int, help="Año de inicio", required=True)
    parser.add_argument("--out", help="Base de datos de salida", required=True)
    args = parser.parse_args()
    if not exists(args.xls):
        sys.exit("No existe --xls %s" % args.xls)
    if (False, False) == (isfile(args.xls), isdir(args.xls)):
        sys.exit("No es un fichero ni un directorio --xls %s" % args.xls)

    reader = Movimientos(
        source=args.xls,
        year=args.ini
    )
    if len(reader.items) == 0:
        sys.exit("No hay movimientos")

    roo_path = join(dirname(realpath(__file__)))
    fix_sql = join(roo_path, "sql/fix")

    with DBIng(args.out, reload=True) as db:
        db.populate(reader)
        for sql in sorted(Path(fix_sql).rglob('*.sql')):
            db.execute(sql)
