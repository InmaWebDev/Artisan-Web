import sqlite3

def init():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Crear tablas si no existen (no se elimina información existente)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT,
            imagen_url TEXT
        )
    ''')

    # Datos iniciales basados en tus archivos; se insertarán sólo si la tabla está vacía
    cursor.execute('SELECT COUNT(*) FROM productos')
    count = cursor.fetchone()[0]
    productos_iniciales = []
    if count == 0:
        productos_iniciales = [
            ('Manilla Delica 3 lineas', 'Bisuteria', 30000, 'Diseño zigzag hecho a mano', '/static/img/productos/Bisuteria/pulseras/pul_mosta_0_1.jpg'),
            ('Calzado Artesanal', 'Calzado', 85000, 'Cuero genuino nacional', '/static/img/productos/Calzado.jpg'),
            ('Bolso Marroquinería', 'Marroquineria', 120000, 'Acabados de lujo', '/static/img/productos/Marroquineria.jpg'),
            ('Decoración Ave Paraíso', 'Decoracion', 45000, 'Base tallada a mano', '/static/img/productos/Decoración/bases aveparaiso/base_aveparaiso_0_1.jpg')
        ]

    cursor.executemany('INSERT INTO productos (nombre, categoria, precio, descripcion, imagen_url) VALUES (?, ?, ?, ?, ?)', productos_iniciales)
    
    # Asegúrate de que exista al menos un admin para entrar al panel
    cursor.execute("INSERT OR IGNORE INTO usuarios (nombre, correo, password, rol) VALUES ('Admin', 'admin@artisan.com', 'admin123', 'admin')")
    
    conn.commit()
    conn.close()
    print("Base de datos sincronizada con productos iniciales.")

if __name__ == '__main__':
    init()