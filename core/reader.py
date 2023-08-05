
import re
from os.path import isdir, isfile
from pathlib import Path
from .movimiento import Movimiento
from functools import cached_property
from dataclasses import dataclass

re_year = re.compile(r"^_?((20|19)\d\d).*")
re_sp = re.compile(r"\s+")


def get_dec(x: float):
    return len(str(float(x)).split(".")[-1])


def safe_sum(*arr) -> float:
    tot = sum(map(lambda x: round(x, 2), arr))
    return round(tot, 2)


@dataclass(frozen=True)
class Reader:
    source: str
    year: int

    @cached_property
    def items(self) -> tuple[Movimiento]:
        items: set[Movimiento] = set()
        index: dict[Movimiento, tuple[int, str]] = {}
        for path in self.iter_path():
            for i, m in enumerate(Movimiento.reader(path)):
                items.add(m)
                if m not in index or index[m][0] > path.name:
                    index[m] = (path.name, i)
        movs = sorted(items, key=lambda m: (m.fecha, index[m]))
        return tuple(movs)

    def iter_path(self):
        if isfile(self.source):
            yield Path(self.source)
        elif isdir(self.source):
            paths = []
            for path in Path(self.source).rglob('*.xls'):
                m = re_year.match(path.name)
                if not m:
                    continue
                year = int(m.group(1))
                if year < self.year:
                    continue
                paths.append((year, path))
            for _, path in sorted(paths):
                yield path

    def get_saldo(self) -> float:
        cuentas: dict[str, Movimiento] = {}
        for m in self.items:
            if m.cuenta not in cuentas:
                cuentas[m.cuenta] = m
        saldo = 0
        for c, m in cuentas.items():
            saldo = safe_sum(saldo, m.saldo, -m.importe)

        return saldo

    @cached_property
    def historia(self):
        arr = []
        saldo = self.get_saldo()
        for m in self.items:
            saldo = safe_sum(saldo, m.importe)
            if not m.is_interno():
                arr.append(m.replace(saldo=saldo))
        return tuple(arr)
