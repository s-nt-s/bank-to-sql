from datetime import date
from typing import NamedTuple
from functools import cache
from .category import SubCategory


class Movimiento(NamedTuple):
    cuenta: str
    fecha: date
    subcategoria: SubCategory
    concepto: str
    importe: float
    saldo: float

    @cache
    def get_categoria(self):
        return self.subcategoria.parent()
