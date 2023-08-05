from .dblite import DBLite, EmptyInsertException
from os.path import dirname, realpath, join
from .movimiento import Movimiento

roo_path = join(dirname(realpath(__file__)), '..')


def _tp(arr):
    arr = set(i for i in arr if i is not None)
    return tuple(sorted(arr))


class DBIng(DBLite):
    def __init__(self, *args, **kvargs):
        super().__init__(*args, **kvargs)
        self.id_txt: dict[str, dict[str, int]] = {}
        if "movimiento" not in self.tables:
            self.execute(join(roo_path, "sql/schema.sql"))
        for table in self.tables:
            if self.is_id_table(table):
                self.id_txt[table] = {}
                for id, txt in self.select("select id, txt from "+table):
                    self.id_txt[table][txt] = id

    def is_id_table(self, table):
        return len(set({"id", "txt"}).intersection(self.get_cols(table))) == 2

    def get_id_from_txt(self, table, txt, **kwargs):
        if txt is None:
            return None
        if self.id_txt[table].get(txt) is None:
            super().insert(table, txt=txt, **kwargs)
            self.id_txt[table][txt] = self.one(f"select id from {table} where txt=?", txt)
        return self.id_txt[table][txt]

    def insert(self, table, **kwargs):
        idTxt = kwargs.get('txt') if table in self.id_txt else None
        if idTxt and self.id_txt[table].get(idTxt):
            return
        for k, v in list(kwargs.items()):
            if k in self.id_txt and isinstance(v, str):
                kwargs[k] = self.get_id_from_txt(k, v)
        try:
            super().insert(table, **kwargs)
        except EmptyInsertException:
            return
        if idTxt:
            self.id_txt[table][idTxt] = self.one(f"select id from {table} where txt=?", idTxt)

    def populate(self, movs: tuple[Movimiento]):
        for c in _tp(m.categoria for m in movs):
            self.insert("categoria", txt=c)
            for s in _tp(m.subcategoria for m in movs if m.categoria==c):
                self.insert("subcategoria", txt=s, categoria=c)
        for m in movs:
            self.insert("movimiento", **m._asdict())
