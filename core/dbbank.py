from .dblite import DBLite, gW, dict_factory, EmptyInsertException
from .movimientos import Movimientos
from core.filemanager import FM
from .category import SubCategory


class DBBank(DBLite):
    def __init__(self, *args, **kvargs):
        super().__init__(*args, **kvargs)
        self.id_txt: dict[str, dict[str, int]] = {}
        if "movimiento" not in self.tables:
            self.execute("sql/schema.sql")
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

        self.set_traspasos_entre_cuentas()
        self.update_devoluciones()

    def set_traspasos_entre_cuentas(self):
        updt = set()
        subcat = str(SubCategory.TRANSACCION_CUENTAS)
        sql = FM.load("sql/traspasos_entre_cuentas.sql")
        for r in self.select(sql, row_factory=dict_factory):
            if r['s_sub'] != subcat:
                updt.add(r["salida"])
            if r['e_sub'] != subcat:
                updt.add(r["entrada"])
        if len(updt) == 0:
            return
        idsub = self.get_id_subcat(SubCategory.TRANSACCION_CUENTAS)
        self.execute(f"UPDATE movimiento SET subcategoria = {idsub} where id "+gW(updt))

    def get_id_subcat(self, sub: SubCategory):
        self.get_id_from_txt("categoria", str(sub.parent()))
        return self.get_id_from_txt("subcategoria", str(sub))

    def update_devoluciones(self):
        for devol in self.iter_devoluciones():
            importe = sum([i for f, i in devol])
            if importe > 0:
                raise ValueError(f"Devolución con importe positivo: {devol} <- {devol}")
            if importe != 0:
                x = devol.pop(0)
                self.execute(f"UPDATE movimiento SET importe = {importe} WHERE (fecha = '{x[0]}' AND importe = {x[1]})")

            self.execute("DELETE FROM movimiento WHERE " + " OR ".join(map(
                lambda x: f"(fecha = '{x[0]}' AND importe = {x[1]})",
                devol
            )))

    def iter_devoluciones(self):
        devol = []
        txt: str = (FM.safe_load("sql/devoluciones.txt") or "").strip()
        for ln in txt.split("\n"):
            ln = ln.strip()
            if len(ln) == 0 or ln[0] == "#":
                continue
            spl = ln.split()
            if len(spl) < 2:
                continue
            fecha, s_importe = spl[:2]
            importe = float(s_importe)
            if importe >= 0 and len(devol) == 0:
                continue
            if importe < 0:
                if len(devol) > 1:
                    yield devol
                devol = []
            devol.append((fecha, importe))
        if len(devol) > 1:
            yield devol
