from .dblite import DBLite
from os.path import dirname, realpath, join

roo_path = join(dirname(realpath(__file__)), '..')

class DBIng(DBLite):
    def __init__(self, *args, **kvargs):
        super().__init__(*args, **kvargs)
        if "movimiento" not in self.tables:
            self.execute(join(roo_path, "sql/schema.sql"))
        self.id_txt = {}
        for table, cols in self.tables.items():
            if tuple(cols) == ("id", "txt"):
                self.id_txt[table] = {}

    def get_id_from_txt(self, table, txt):
        if self.id_txt[table].get(txt) is None:
            super().insert(table, txt=txt)
            self.id_txt[table][txt] = super().one("select id from "+table+" where txt=?", txt)
        return self.id_txt[table][txt]

    def set_movimiento(self, movimiento):
        mov = dict(movimiento.__dict__)
        for k, v in list(mov.items()):
            if k in self.id_txt:
                mov[k] = self.get_id_from_txt(k, v)
        super().insert("movimiento", **mov)
