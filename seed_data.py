import os
from werkzeug.security import generate_password_hash
from database_setup import setup
from db_utils import connect_db, using_postgres


def seed(admin_email=None, admin_password=None):
    setup()
    db = connect_db()
    cursor = db.conn.cursor()
    if admin_email and admin_password:
        try:
            hp = generate_password_hash(admin_password)
            if using_postgres():
                cursor.execute(
                    'INSERT INTO usuarios (nombre, correo, password, rol) VALUES (%s, %s, %s, %s) ON CONFLICT (correo) DO NOTHING',
                    ('Admin', admin_email, hp, 'admin')
                )
            else:
                cursor.execute(
                    'INSERT OR IGNORE INTO usuarios (nombre, correo, password, rol) VALUES (?, ?, ?, ?)',
                    ('Admin', admin_email, hp, 'admin')
                )
            print('Admin creado/ignore si ya existía:', admin_email)
        except Exception as e:
            print('Error creando admin:', e)
    try:
        if using_postgres():
            cursor.execute('INSERT INTO categorias (nombre) VALUES (%s) ON CONFLICT DO NOTHING', ('Ejemplos',))
            cursor.execute(
                'INSERT INTO productos (id, nombre, categoria, precio, descripcion, imagen_url) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING',
                (1, 'Producto de ejemplo', 'Ejemplos', 19.99, 'Producto de ejemplo creado para pruebas.', 'static/img/productos/example.jpg')
            )
        else:
            cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES ('Ejemplos')")
            cursor.execute(
                'INSERT OR IGNORE INTO productos (id, nombre, categoria, precio, descripcion, imagen_url) VALUES (?,?,?,?,?,?)',
                (1, 'Producto de ejemplo', 'Ejemplos', 19.99, 'Producto de ejemplo creado para pruebas.', 'static/img/productos/example.jpg')
            )
        print('Producto de ejemplo creado (id=1)')
    except Exception as e:
        print('Error creando producto de ejemplo:', e)
    db.commit()
    db.close()


if __name__ == '__main__':
    seed(os.environ.get('INITIAL_ADMIN_EMAIL'), os.environ.get('INITIAL_ADMIN_PASSWORD'))

if __name__ == '__main__':
    seed(os.environ.get('INITIAL_ADMIN_EMAIL'), os.environ.get('INITIAL_ADMIN_PASSWORD'))
