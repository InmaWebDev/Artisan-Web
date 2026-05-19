import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Ver todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"✅ Tablas creadas: {tables}")

# Verificar admin
cursor.execute("SELECT correo, password FROM usuarios WHERE correo='admin@artisan.com'")
row = cursor.fetchone()
if row:
    print(f"✅ Admin encontrado: {row[0]}")
    print(f"✅ Contraseña hasheada: {row[1][:40]}...")
else:
    print("❌ Admin no encontrado")

# Verificar estructura de pedidos
cursor.execute("PRAGMA table_info(pedidos)")
cols = cursor.fetchall()
print(f"\n✅ Columnas en tabla 'pedidos':")
for col in cols:
    print(f"   - {col[1]} ({col[2]})")

conn.close()
print("\n✅ Base de datos verificada correctamente")
