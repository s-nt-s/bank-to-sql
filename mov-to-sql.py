#!/usr/bin/env python3

import argparse
from os.path import dirname, isdir, isfile, exists, realpath, join
from pathlib import Path
import sys
from core.dbbank import DBBank
from core.movimientos import Movimientos
from core.log import config_log

config_log("mov-to-sql.log")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Genera base de datos sqlite a partir de movimientos bancarios')
    parser.add_argument("--mov", help="Carpeta o fichero donde buscar los movimientos", required=True)
    parser.add_argument("--ini", type=int, help="Año de inicio", required=True)
    parser.add_argument("--out", help="Base de datos de salida", required=True)
    args = parser.parse_args()
    if not exists(args.mov):
        sys.exit("No existe --mov %s" % args.mov)
    if (False, False) == (isfile(args.mov), isdir(args.mov)):
        sys.exit("No es un fichero ni un directorio --mov %s" % args.mov)

    reader = Movimientos(
        source=args.mov,
        year=args.ini
    )
    if len(reader.items) == 0:
        sys.exit("No hay movimientos")

    roo_path = join(dirname(realpath(__file__)))
    fix_sql = join(roo_path, "sql/fix")

    with DBBank(args.out, reload=True) as db:
        db.populate(reader)
        for sql in sorted(Path(fix_sql).rglob('*.sql')):
            db.execute(sql)
