
import re
from os.path import isdir, isfile
from pathlib import Path
from .movimiento import Movimiento
from functools import cached_property
from dataclasses import dataclass
from datetime import date
from core.reader import Reader, IsNotForMeException
from typing import Generator
import logging
from .category import SubCategory, Category

logger = logging.getLogger(__name__)

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


def rglob(path: Path, *ext):
    for e in ext:
        yield from path.rglob("*."+e)


@dataclass(frozen=True)
class Movimientos:
    source: str
    year: int

    @cached_property
    def items(self) -> tuple[Movimiento]:
        items: set[Movimiento] = set()
        index: dict[Movimiento, tuple[str, int]] = {}
        for path in self.iter_path():
            reader = self.__get_reader(path)
            if reader is None:
                continue
            for i, m in enumerate(reader.read()):
                if m.importe == 0:
                    continue
                items.add(m)
                if m not in index or index[m][0] > path.name:
                    index[m] = (path.name, i)
        movs = sorted(items, key=lambda m: (m.fecha, index[m]))

        def s_key(m: Movimiento):
            k = [m.fecha, movs.index(m)]
            return tuple(k)
        movs = sorted(movs, key=s_key)
        return tuple(movs)

    def iter_path(self) -> Generator[Path, None, None]:
        if isfile(self.source):
            yield Path(self.source)
        elif isdir(self.source):
            src = Path(self.source)
            paths = []
            path: Path
            for path in rglob(src, 'xls', 'xlsx', 'pdf'):
                m = re_year.match(path.name)
                if not m:
                    continue
                year = int(m.group(1))
                if year < self.year:
                    continue
                paths.append((year, path))
            for _, path in sorted(paths):
                yield path

    def __get_reader(self, path: Path) -> Reader:
        for cls in Reader.get_subclasses():
            try:
                return cls(path)
            except IsNotForMeException:
                continue
        logger.info(f"KO   {path}")
        return None

    @cached_property
    def inicio(self) -> tuple[Movimiento]:
        arr = []
        done = set()
        for m in self.items:
            if m.cuenta in done:
                continue
            done.add(m.cuenta)
            saldo = safe_sum(m.saldo, -m.importe)
            if saldo > 0:
                arr.append(Movimiento(
                    cuenta=m.cuenta,
                    fecha=date(m.fecha.year-1, 12, 31),
                    subcategoria=SubCategory.SALDO_INICIAL,
                    concepto=str(SubCategory.SALDO_INICIAL),
                    importe=saldo,
                    saldo=saldo
                ))
        return tuple(arr)

    @cached_property
    def movimientos(self) -> tuple[Movimiento]:
        return self.inicio + self.items

    def iter_categorias(self):
        cat: dict[Category, set[SubCategory]] = {}
        for m in self.movimientos:
            c = m.get_categoria()
            if c not in cat:
                cat[c] = set()
            cat[c].add(m.subcategoria)

        for c in sorted(cat.keys(), key=lambda c: str(c)):
            sub = sorted(cat[c], key=lambda s: str(s))
            if len(sub) > 0:
                yield c, sub
