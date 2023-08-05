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
  categoria INTEGER,
  FOREIGN KEY(categoria) REFERENCES categoria(id)
);

CREATE TABLE movimiento (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cuenta INTEGER,
  fecha DATE,
  subcategoria INTEGER,
  concepto TEXT,
  importe NUMBER,
  saldo NUMBER,
  FOREIGN KEY(cuenta) REFERENCES cuenta(id),
  FOREIGN KEY(subcategoria) REFERENCES subcategoria(id)
);

CREATE TABLE tipo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txt TEXT
);

CREATE TABLE tipado (
  movimiento INTEGER NOT NULL,
  tipo INTEGER NOT NULL,
  FOREIGN KEY(movimiento) REFERENCES movimiento(id),
  FOREIGN KEY(tipo) REFERENCES tipo(id)
)


