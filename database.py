import sqlite3

# Crear conexión
conn = sqlite3.connect("flota.db")

cursor = conn.cursor()

# Crear tabla
cursor.execute("""
CREATE TABLE IF NOT EXISTS vehiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placa TEXT,
    tipo TEXT,
    estado TEXT
    kilometraje REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rutas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origen TEXT,
    destino TEXT,
    distancia REAL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS viajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origen TEXT,
    destino TEXT,
    vehiculo TEXT,
    distancia REAL,
    costo REAL,
    tiempo TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    password TEXT
)
""")
cursor.execute("""
INSERT INTO usuarios (usuario, password)
SELECT 'admin', '1234'
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios
    WHERE usuario='admin'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    origen TEXT,
    destino TEXT,
    peso REAL,
    estado TEXT
)
""")

conn.commit()

conn.close()

print("Base de datos creada correctamente")