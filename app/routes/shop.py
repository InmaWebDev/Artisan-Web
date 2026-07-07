from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.db import get_db

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/')
def home():
    return redirect(url_for('shop.index'))


@shop_bp.route('/index')
def index():
    db = get_db()
    cats = db.execute('SELECT * FROM categorias').fetchall()
    return render_template('index.html', categorias=cats)


@shop_bp.route('/lineaproductos')
def lineaproductos():
    cat_sel = request.args.get('categoria')
    nombre_sel = request.args.get('nombre')

    db = get_db()
    cats = db.execute('SELECT * FROM categorias').fetchall()

    if cat_sel:
        nombres = db.execute(
            'SELECT DISTINCT nombre FROM productos WHERE categoria = ? AND parent_id IS NULL',
            (cat_sel,)
        ).fetchall()
    else:
        nombres = db.execute(
            'SELECT DISTINCT nombre FROM productos WHERE parent_id IS NULL'
        ).fetchall()

    conditions = ['parent_id IS NULL']
    params = []
    if cat_sel:
        conditions.append('categoria = ?')
        params.append(cat_sel)
    if nombre_sel:
        conditions.append('nombre = ?')
        params.append(nombre_sel)

    query = 'SELECT * FROM productos WHERE ' + ' AND '.join(conditions) + ' ORDER BY id DESC'
    prods = db.execute(query, params).fetchall()

    return render_template('lineaproductos.html', productos=prods, categorias=cats,
                           nombres=nombres, categoria_actual=cat_sel,
                           nombre_actual=nombre_sel)


@shop_bp.route('/producto/<int:id>')
def producto_detalle(id):
    db = get_db()
    p = db.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    if not p:
        flash('Producto no encontrado.', 'error')
        return redirect(url_for('shop.lineaproductos'))

    subs = db.execute('SELECT * FROM productos WHERE parent_id = ?', (id,)).fetchall()
    return render_template('producto.html', p=p, subproductos=subs)
