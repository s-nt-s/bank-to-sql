
import re
from os.path import isdir, isfile
from pathlib import Path
from .movimiento import Movimiento
from functools import cached_property
from dataclasses import dataclass
from datetime import date

re_year = re.compile(r"^_?((20|19)\d\d).*")
re_sp = re.compile(r"\s+")


def _tp(arr):
    arr = set(i for i in arr if i is not None)
    return tuple(sorted(arr))


def get_dec(x: float):
    return len(str(float(x)).split(".")[-1])


def safe_sum(*arr) -> float:
    tot = sum(map(lambda x: round(x, 2), arr))
    return round(tot, 2)


@dataclass(frozen=True)
class Movimientos:
    source: str
    year: int

    @staticmethod
    def set_interno(arr: list[Movimiento]):
        index: dict[Movimiento, int] = {}
        dts: dict[date, list[Movimiento]] = {}
        for i, m in enumerate(arr):
            if m.maybe_interno:
                if m.fecha not in dts:
                    dts[m.fecha] = []
                dts[m.fecha].append(m)
                index[m] = i
        ok: list[Movimiento] = []
        for movs in dts.values():
            while len(movs) > 1:
                m = movs.pop()
                for x in movs:
                    if m.is_traspaso(x):
                        movs.remove(x)
                        ok.append(m)
                        ok.append(x)
        for m in ok:
            arr[index[m]] = m.replace(
                categoria="Transacción entre cuentas",
                subcategoria="Transacción entre cuentas",
                interno=True
            )

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
        Movimientos.set_interno(movs)

        def s_key(m: Movimiento):
            k = [m.fecha, not m.interno, 0, 0, movs.index(m)]
            if m.interno:
                k[2] = abs(m.importe)
                k[3] = m.importe
            return tuple(k)
        movs = sorted(movs, key=s_key)
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

    @cached_property
    def inicio(self) -> tuple[Movimiento]:
        arr = []
        done = set()
        saldo_inicial = "Saldo inicial"
        for m in self.items:
            if m.cuenta in done:
                continue
            done.add(m.cuenta)
            saldo = safe_sum(m.saldo, -m.importe)
            if saldo > 0:
                arr.append(Movimiento(
                    cuenta=m.cuenta,
                    fecha=date(m.fecha.year-1, 12, 31),
                    categoria=saldo_inicial,
                    subcategoria=saldo_inicial,
                    concepto=saldo_inicial,
                    importe=saldo,
                    saldo=saldo
                ))
        return tuple(arr)

    @cached_property
    def movimientos(self) -> tuple[Movimiento]:
        return self.inicio + self.items
    
    @cached_property
    def historia(self) -> tuple[Movimiento]:
        arr = []
        saldo = 0
        for m in self.movimientos:
            saldo = safe_sum(saldo, m.importe)
            if not m.interno:
                arr.append(m.replace(saldo=saldo))
        return tuple(arr)

    def iter_categorias(self):
        for c in _tp(m.categoria for m in self.movimientos):
            sub = _tp(m.subcategoria for m in self.movimientos if m.categoria==c)
            if len(sub) > 0:
                yield c, sub
