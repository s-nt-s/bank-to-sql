from pathlib import Path
from core.movimiento import Movimiento
from typing import Generator, Any
import logging

import importlib
import pkgutil
from functools import cache

logger = logging.getLogger(__name__)


class IsNotForMeException(Exception):
    pass


class Reader:
    def __init__(self, path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(str(path))
        self.path = path
        self._check_file()
        logger.info(f"{self.__class__.__name__} {path}")

    @staticmethod
    def get_path(path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(str(path))
        return path

    def read(self) -> Generator[Movimiento, Any, None]:
        raise NotImplementedError("You must use a subclass")

    def _check_file(self):
        raise NotImplementedError("You must use a subclass")

    @cache
    @staticmethod
    def get_subclasses():
        package = importlib.import_module(__name__)
        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            md = f"{__name__}.{module_name}"
            logger.info(f"import {md}")
            importlib.import_module(md)
        return Reader.__subclasses__()
