from .dblite import DBLite, EmptyInsertException
from os.path import dirname, realpath, join
from .movimientos import Movimientos

roo_path = join(dirname(realpath(__file__)), '..')


class DBBank(DBLite):
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
            id = self.one(f"select id from {table} where txt=?", txt)
            self.id_txt[table][txt] = id
        return self.id_txt[table][txt]

    def insert(self, table, **kwargs):
        idTxt = kwargs.get('txt') if table in self.id_txt else None
        if idTxt and idTxt in self.id_txt[table]:
            return
        for k, v in list(kwargs.items()):
            if k in self.id_txt and isinstance(v, str):
                kwargs[k] = self.get_id_from_txt(k, v)
        try:
            super().insert(table, **kwargs)
        except EmptyInsertException:
            return
        if idTxt:
            id = self.one(f"select id from {table} where txt=?", idTxt)
            self.id_txt[table][idTxt] = id

    def populate(self, reader: Movimientos):
        for c, sub in reader.iter_categorias():
            self.insert("categoria", txt=str(c))
            for s in sub:
                self.insert("subcategoria", txt=str(s), categoria=str(c))
        for m in reader.movimientos:
            mov = m._asdict()
            mov["categoria"] = str(m.get_categoria())
            mov["subcategoria"] = str(m.subcategoria)
            self.insert("movimiento", **mov)
