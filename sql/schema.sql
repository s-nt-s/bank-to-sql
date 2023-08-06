CREATE TABLE cuenta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL
);
CREATE TABLE categoria (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL UNIQUE
);
CREATE TABLE subcategoria (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL UNIQUE,
  categoria INTEGER NOT NULL DEFAULT -1,
  FOREIGN KEY(categoria) REFERENCES categoria(id)
);

CREATE TABLE movimiento (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cuenta INTEGER,
  fecha DATE,
  subcategoria INTEGER NOT NULL DEFAULT -1,
  concepto TEXT,
  importe NUMBER,
  FOREIGN KEY(cuenta) REFERENCES cuenta(id),
  FOREIGN KEY(subcategoria) REFERENCES subcategoria(id)
);

insert into categoria (id, txt) values
(-1, 'Sin categoria');
insert into subcategoria (id, txt, categoria) values
(-1, 'Sin subcategoria', -1);