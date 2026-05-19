import os
import time
import json
from urllib.parse import quote
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from db_utils import connect_db, ensure_schema

load_dotenv()

app = Flask(__name__)
# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
)
limiter.init_app(app)
# SECRET_KEY must be provided in production via env
secret = os.environ.get('SECRET_KEY') or os.environ.get('SECRET', None)
if os.environ.get('FLASK_ENV') == 'production' and not secret:
    raise RuntimeError('SECRET_KEY is required in production. Set SECRET_KEY in environment.')
app.secret_key = secret or os.environ.get('SECRET_KEY', 'artisan_key_2026')
app.config['UPLOAD_FOLDER'] = 'static/img/productos'
WHATSAPP_PHONE = os.environ.get('WHATSAPP_PHONE', '573123580705').lstrip('+').strip()

# Harden session cookies in production
if os.environ.get('FLASK_ENV') == 'production':
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )

# custom Jinja filter for newlines to <br>
def nl2br(value):
    return value.replace("\n", "<br>")
app.jinja_env.filters['nl2br'] = nl2br
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    conn = connect_db()
    ensure_schema(conn)
    return conn

# --- RUTAS DE ACCESO ---
@app.route('/')
def home():
    # Página principal pública: redirige a la tienda
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')
        
        if not correo or not password:
            flash('Por favor completa todos los campos.', 'error')
            return render_template('login.html')
        
        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE correo=?', (correo,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session.update({'user_id': user['id'], 'rol': user['rol'], 'nombre': user['nombre']})
            flash('Bienvenido, has iniciado sesión correctamente.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos.', 'error')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('password_confirm', '')
        
        # Validaciones
        if not all([nombre, correo, password, confirm]):
            flash('Por favor completa todos los campos.', 'error')
            return render_template('registro.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('registro.html')
        
        if password != confirm:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('registro.html')
        
        if len(nombre) < 3:
            flash('El nombre debe tener al menos 3 caracteres.', 'error')
            return render_template('registro.html')
        
        db = get_db()
        try:
            hashed_pwd = generate_password_hash(password)
            db.execute('INSERT INTO usuarios (nombre, correo, password, rol) VALUES (?, ?, ?, ?)',
                       (nombre, correo, hashed_pwd, 'cliente'))
            db.commit()
            flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('El correo ya está registrado.', 'error')
        finally:
            db.close()
    return render_template('registro.html')

# --- TIENDA ---
@app.route('/index')
def index():
    # La tienda es pública; si el usuario está logueado se mantiene la sesión
    db = get_db()
    cats = db.execute('SELECT * FROM categorias').fetchall()
    db.close()
    return render_template('index.html', categorias=cats, ts=int(time.time()))

@app.route('/lineaproductos')
def lineaproductos():
    """Show the product listing with optional category/name filters.

    Two query parameters are supported:
      * categoria  --> exact match against the categoria column
      * nombre     --> exact match against the nombre column
    The dropdowns in the template are populated from the database so that
    users can select the values rather than typing them.
    """
    cat_sel = request.args.get('categoria')
    nombre_sel = request.args.get('nombre')

    db = get_db()
    cats = db.execute('SELECT * FROM categorias').fetchall()
    if cat_sel:
        nombres = db.execute('SELECT DISTINCT nombre FROM productos WHERE categoria = ? AND parent_id IS NULL', (cat_sel,)).fetchall()
    else:
        nombres = db.execute('SELECT DISTINCT nombre FROM productos WHERE parent_id IS NULL').fetchall()

    # build query conditionally
    query = 'SELECT * FROM productos'
    order = ' ORDER BY id DESC'
    params = []
    conditions = []
    if cat_sel:
        conditions.append('categoria = ?')
        params.append(cat_sel)
    # hide subproducts in any listing; they only appear on a product detail page
    conditions.append('parent_id IS NULL')
    if nombre_sel:
        conditions.append('nombre = ?')
        params.append(nombre_sel)
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    prods = db.execute(query + order, params).fetchall()
    db.close()
    return render_template('lineaproductos.html', productos=prods, categorias=cats,
                           nombres=nombres, categoria_actual=cat_sel,
                           nombre_actual=nombre_sel, ts=int(time.time()))

@app.route('/producto/<int:id>')
def producto_detalle(id):
    db = get_db()
    p = db.execute('SELECT * FROM productos WHERE id=?', (id,)).fetchone()
    if not p:
        db.close()
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('lineaproductos'))
    subs = db.execute('SELECT * FROM productos WHERE parent_id=?', (id,)).fetchall()
    db.close()
    return render_template('producto.html', p=p, subproductos=subs, ts=int(time.time()), whatsapp_phone=WHATSAPP_PHONE)

# --- PANEL ADMIN ---
@app.route('/admin')
def admin_panel():
    # only admins can access the panel
    if session.get('rol') != 'admin':
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('login'))
    db = get_db()
    # join to get parent name
    prods = db.execute('''SELECT p.*, parent.nombre AS parent_name
                          FROM productos p
                          LEFT JOIN productos parent ON p.parent_id = parent.id
                          ORDER BY p.parent_id IS NOT NULL, p.id DESC''').fetchall()
    cats = db.execute('SELECT * FROM categorias').fetchall()
    # Cargar pedidos ordenados por fecha descendente
    pedidos_rows = db.execute('SELECT * FROM pedidos ORDER BY fecha_creacion DESC').fetchall()
    pedidos = []
    for row in pedidos_rows:
        pedido = dict(row)
        try:
            pedido['items'] = json.loads(pedido['items']) if pedido['items'] else []
        except Exception:
            pedido['items'] = []
        pedido['item_count'] = len(pedido['items'])
        pedidos.append(pedido)
    db.close()
    parent_prefill = request.args.get('parent_id')
    return render_template('admin.html', productos=prods, categorias=cats, parent_prefill=parent_prefill, pedidos=pedidos, ts=int(time.time()))

@app.route('/admin/add_prod', methods=['POST'])
def add_product():
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    
    # Validaciones
    nombre = request.form.get('nombre', '').strip()
    categoria = request.form.get('categoria', '').strip()
    precio_str = request.form.get('precio', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    
    if not all([nombre, categoria, precio_str, descripcion]):
        flash('Por favor completa todos los campos obligatorios.', 'error')
        return redirect(url_for('admin_panel'))
    
    try:
        precio = float(precio_str)
        if precio <= 0:
            raise ValueError
    except:
        flash('El precio debe ser un número positivo.', 'error')
        return redirect(url_for('admin_panel'))
    
    imgs = []
    for i in range(1, 4):
        f = request.files.get(f'img{i}')
        if f and f.filename != '':
            fname = secure_filename(f"{nombre}_{i}_{f.filename}")
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            imgs.append(f"/static/img/productos/{fname}")
        else:
            imgs.append(None)
    
    parent = request.form.get('parent_id') or None
    db = get_db()
    try:
        db.execute('INSERT INTO productos (nombre, categoria, precio, descripcion, imagen_url, img2, img3, parent_id) VALUES (?,?,?,?,?,?,?,?)',
                   (nombre, categoria, precio, descripcion, imgs[0], imgs[1], imgs[2], parent))
        db.commit()
        flash('Producto publicado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al guardar el producto.', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/cat/add', methods=['POST'])
def add_category():
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    
    nueva_categoria = request.form.get('nueva_categoria', '').strip()
    if not nueva_categoria:
        flash('El nombre de la categoría no puede estar vacío.', 'error')
    else:
        db = get_db()
        try:
            if os.environ.get('DATABASE_URL', '').startswith('postgres'):
                db.execute('INSERT INTO categorias (nombre) VALUES (%s) ON CONFLICT DO NOTHING', (nueva_categoria,))
            else:
                db.execute('INSERT OR IGNORE INTO categorias (nombre) VALUES (?)', (nueva_categoria,))
            db.commit()
            flash('Categoría creada exitosamente.', 'success')
        except Exception:
            flash('Error al crear la categoría.', 'error')
        finally:
            db.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/cat/del/<int:id>')
def delete_category(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    try:
        db.execute('DELETE FROM categorias WHERE id=?', (id,))
        db.commit()
        flash('Categoría eliminada.', 'success')
    except:
        flash('Error al eliminar la categoría.', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/prod/del/<int:id>')
def delete_product(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    try:
        db.execute('DELETE FROM productos WHERE id=?', (id,))
        db.commit()
        flash('Producto eliminado.', 'success')
    except:
        flash('Error al eliminar el producto.', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/prod/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        # update fields; handle new images if uploaded
        nombre = request.form.get('nombre', '').strip()
        categoria = request.form.get('categoria', '').strip()
        precio_str = request.form.get('precio', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if not all([nombre, categoria, precio_str, descripcion]):
            flash('Por favor completa todos los campos obligatorios.', 'error')
            db.close()
            return redirect(url_for('admin_panel'))
        
        try:
            precio = float(precio_str)
            if precio <= 0:
                raise ValueError
        except:
            flash('El precio debe ser un número positivo.', 'error')
            db.close()
            return redirect(url_for('admin_panel'))
        
        imgs = []
        for i in range(1, 4):
            f = request.files.get(f'img{i}')
            if f and f.filename != '':
                fname = secure_filename(f"{nombre}_{i}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                imgs.append(f"/static/img/productos/{fname}")
            else:
                imgs.append(request.form.get(f'old_img{i}'))
        parent = request.form.get('parent_id') or None
        
        try:
            db.execute('''UPDATE productos SET nombre=?, categoria=?, precio=?, descripcion=?,
                          imagen_url=?, img2=?, img3=?, parent_id=? WHERE id=?''',
                       (nombre, categoria, precio, descripcion, imgs[0], imgs[1], imgs[2], parent, id))
            db.commit()
            flash('Producto actualizado exitosamente.', 'success')
        except Exception as e:
            flash('Error al actualizar el producto.', 'error')
        finally:
            db.close()
        return redirect(url_for('admin_panel'))
    else:
        prod = db.execute('SELECT * FROM productos WHERE id=?', (id,)).fetchone()
        cats = db.execute('SELECT * FROM categorias').fetchall()
        prods = db.execute('SELECT id, nombre, parent_id FROM productos').fetchall()
        db.close()
        return render_template('edit_product.html', p=prod, categorias=cats, productos=prods)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))

#========== carrito routes ==========
@app.route('/carrito')
def view_cart():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver el carrito.', 'error')
        return redirect(url_for('login'))
    items = session.get('cart', [])
    total = sum(item['precio'] * item.get('cantidad',1) for item in items)
    return render_template('carrito.html', items=items, total=total)

@app.route('/carrito/add/<int:id>')
def add_to_cart(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para agregar productos al carrito.', 'error')
        return redirect(url_for('login'))
    
    try:
        qty = int(request.args.get('cantidad', 1))
        if qty < 1:
            qty = 1
        if qty > 1000:
            qty = 1000
    except:
        qty = 1
    
    db = get_db()
    p = db.execute('SELECT id,nombre,precio FROM productos WHERE id=? AND parent_id IS NULL', (id,)).fetchone()
    db.close()
    
    if p:
        cart = session.get('cart', [])
        # look for existing item
        for item in cart:
            if item['id'] == p['id']:
                item['cantidad'] = min(item.get('cantidad', 1) + qty, 1000)
                break
        else:
            cart.append({'id': p['id'], 'nombre': p['nombre'], 'precio': p['precio'], 'cantidad': qty})
        session['cart'] = cart
        flash(f"{p['nombre']} agregado al carrito (x{qty})", 'success')
    else:
        flash('Producto no encontrado.', 'error')
    return redirect(request.referrer or url_for('lineaproductos'))

@app.route('/carrito/remove/<int:id>')
def remove_from_cart(id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != id]
    session['cart'] = cart
    flash('Artículo eliminado del carrito.', 'info')
    return redirect(url_for('view_cart'))

@app.route('/carrito/update/<int:id>')
def update_cart(id):
    try:
        qty = int(request.args.get('cantidad', 1))
        if qty < 1:
            qty = 1
        if qty > 1000:  # Límite de cantidad
            qty = 1000
    except:
        qty = 1
    
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == id:
            item['cantidad'] = qty
            flash(f"Cantidad de {item['nombre']} ajustada a {qty}", 'info')
            break
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/carrito/clear')
def clear_cart():
    session.pop('cart', None)
    flash('Carrito vaciado.', 'info')
    return redirect(url_for('view_cart'))

@app.route('/carrito/checkout', methods=['POST'])
def checkout_whatsapp():
    """Registra el pedido y redirija a WhatsApp"""
    if 'user_id' not in session:
        flash('Debes iniciar sesión para comprar.', 'error')
        return redirect(url_for('login'))
    
    cart = session.get('cart', [])
    if not cart:
        flash('Tu carrito está vacío.', 'error')
        return redirect(url_for('view_cart'))
    
    # Calcular total y validar
    try:
        total = sum(item['precio'] * item.get('cantidad', 1) for item in cart)
        if total <= 0:
            raise ValueError("Total inválido")
    except Exception as e:
        flash('Error al procesar el carrito.', 'error')
        return redirect(url_for('view_cart'))
    
    # Obtener datos del usuario
    db = get_db()
    try:
        user = db.execute('SELECT * FROM usuarios WHERE id=?', (session['user_id'],)).fetchone()
        
        if not user:
            flash('Usuario no encontrado.', 'error')
            return redirect(url_for('login'))
        
        # Generar número de orden
        order_num = f"ORD-{int(time.time())}"
        
        # Guardar pedido en BD
        db.execute('''INSERT INTO pedidos (numero_orden, usuario_id, usuario_nombre, items, total, estado)
                      VALUES (?, ?, ?, ?, ?, 'pendiente')''',
                   (order_num, session['user_id'], user['nombre'], json.dumps(cart), total))
        db.commit()
        
        # Construir mensaje para WhatsApp
        msg_items = "\n".join([f"• {item['nombre']} x{item.get('cantidad', 1)} = ${item['precio'] * item.get('cantidad', 1):,.0f}" 
                               for item in cart])
        msg = f"""Hola, me gustaría completar mi compra:

*Número de Orden:* {order_num}

*Items:*
{msg_items}

*Total:* ${total:,.0f}

Por favor confirmar disponibilidad y detalles de pago."""
        
        # Redirigir a WhatsApp con el mensaje usando encoding correcto
        whatsapp_url = f"https://api.whatsapp.com/send?phone={WHATSAPP_PHONE}&text={quote(msg)}"
        
        # Limpiar carrito después de crear el pedido
        session.pop('cart', None)
        
        return redirect(whatsapp_url)
        
    except Exception as e:
        flash(f'Error al procesar la compra.', 'error')
        return redirect(url_for('view_cart'))
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=False)
