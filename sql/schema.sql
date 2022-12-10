CREATE TABLE cuenta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL
);
CREATE TABLE categoria (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL
);
CREATE TABLE subcategoria (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT NOT NULL
);

CREATE TABLE movimiento (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cuenta INTEGER,
  fecha DATE,
  categoria TEXT,
  subcategoria TEXT,
  concepto TEXT,
  importe NUMBER,
  saldo NUMBER,
  FOREIGN KEY(cuenta) REFERENCES cuenta(id),
  FOREIGN KEY(categoria) REFERENCES categoria(id),
  FOREIGN KEY(subcategoria) REFERENCES subcategoria(id)
);
