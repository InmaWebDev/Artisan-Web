import os
from werkzeug.security import generate_password_hash
from db_utils import connect_db, ensure_schema, using_postgres


def setup():
    db = connect_db()
    ensure_schema(db)

    cursor = db.conn.cursor()
    # Admin inicial si se proporcionan variables de entorno
    admin_email = os.environ.get('INITIAL_ADMIN_EMAIL')
    admin_password = os.environ.get('INITIAL_ADMIN_PASSWORD')
    if admin_email and admin_password:
        try:
            admin_pwd = generate_password_hash(admin_password)
            if using_postgres():
                cursor.execute(
                    'INSERT INTO usuarios (nombre, correo, password, rol) VALUES (%s, %s, %s, %s) ON CONFLICT (correo) DO NOTHING',
                    ('Admin', admin_email, admin_pwd, 'admin')
                )
            else:
                cursor.execute(
                    'INSERT OR IGNORE INTO usuarios (nombre, correo, password, rol) VALUES (?, ?, ?, ?)',
                    ('Admin', admin_email, admin_pwd, 'admin')
                )
        except Exception:
            pass

    # Categorías iniciales
    try:
        if using_postgres():
            cursor.execute(
                'INSERT INTO categorias (nombre) VALUES (%s), (%s) ON CONFLICT DO NOTHING',
                ('Bisutería', 'Marroquinería')
            )
        else:
            cursor.execute(
                "INSERT OR IGNORE INTO categorias (nombre) VALUES ('Bisutería'), ('Marroquinería')"
            )
    except Exception:
        pass

    db.commit()
    db.close()
    print('Base de datos lista.')

if __name__ == '__main__':
    setup()