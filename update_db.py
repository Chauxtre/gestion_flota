import sqlite3

conn = sqlite3.connect("flota.db")

cursor = conn.cursor()

try:

    cursor.execute("""
    ALTER TABLE vehiculos
    ADD COLUMN kilometraje REAL DEFAULT 0
    """)

    print("✅ Columna kilometraje agregada")

except:

    print("⚠️ La columna ya existe")

conn.commit()

conn.close()