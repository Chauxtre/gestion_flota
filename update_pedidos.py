import sqlite3

conn = sqlite3.connect("flota.db")

cursor = conn.cursor()

try:

    cursor.execute("""
    ALTER TABLE pedidos
    ADD COLUMN vehiculo TEXT
    """)

    print("✅ Columna vehiculo agregada")

except:

    print("⚠️ La columna ya existe")

conn.commit()

conn.close()