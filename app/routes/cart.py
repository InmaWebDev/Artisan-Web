import json
import time
from urllib.parse import quote

from flask import Blueprint, render_template, request, redirect, session, url_for, flash

from app import WHATSAPP_PHONE
from app.db import get_db
from app.csrf import validate_csrf

cart_bp = Blueprint('cart', __name__)

MAX_QTY = 1000


def cart_required(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para ver el carrito.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper


@cart_bp.route('/carrito')
@cart_required
def view_cart():
    items = session.get('cart', [])
    total = sum(item['precio'] * item.get('cantidad', 1) for item in items)
    return render_template('carrito.html', items=items, total=total)


@cart_bp.route('/carrito/add/<int:id>', methods=['POST'])
@cart_required
def add_to_cart(id):
    if not validate_csrf():
        return redirect(request.referrer or url_for('shop.lineaproductos'))

    try:
        qty = int(request.form.get('cantidad', 1))
        qty = max(1, min(qty, MAX_QTY))
    except (ValueError, TypeError):
        qty = 1

    db = get_db()
    p = db.execute(
        'SELECT id, nombre, precio FROM productos WHERE id = ? AND parent_id IS NULL',
        (id,)
    ).fetchone()

    if not p:
        flash('Producto no encontrado.', 'error')
        return redirect(request.referrer or url_for('shop.lineaproductos'))

    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == p['id']:
            item['cantidad'] = min(item.get('cantidad', 1) + qty, MAX_QTY)
            break
    else:
        cart.append({'id': p['id'], 'nombre': p['nombre'], 'precio': p['precio'], 'cantidad': qty})

    session['cart'] = cart
    flash(f"{p['nombre']} agregado al carrito (x{qty})", 'success')
    return redirect(request.referrer or url_for('shop.lineaproductos'))


@cart_bp.route('/carrito/remove/<int:id>', methods=['POST'])
def remove_from_cart(id):
    if not validate_csrf():
        return redirect(url_for('cart.view_cart'))
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['id'] != id]
    flash('Artículo eliminado del carrito.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/carrito/update/<int:id>', methods=['POST'])
def update_cart(id):
    if not validate_csrf():
        return redirect(url_for('cart.view_cart'))

    try:
        qty = int(request.form.get('cantidad', 1))
        qty = max(1, min(qty, MAX_QTY))
    except (ValueError, TypeError):
        qty = 1

    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == id:
            item['cantidad'] = qty
            flash(f"Cantidad de {item['nombre']} ajustada a {qty}", 'info')
            break
    session['cart'] = cart
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/carrito/clear', methods=['POST'])
def clear_cart():
    if not validate_csrf():
        return redirect(url_for('cart.view_cart'))
    session.pop('cart', None)
    flash('Carrito vaciado.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/carrito/checkout', methods=['POST'])
def checkout_whatsapp():
    if not validate_csrf():
        return redirect(url_for('cart.view_cart'))

    if 'user_id' not in session:
        flash('Debes iniciar sesión para comprar.', 'error')
        return redirect(url_for('auth.login'))

    cart = session.get('cart', [])
    if not cart:
        flash('Tu carrito está vacío.', 'error')
        return redirect(url_for('cart.view_cart'))

    # Recalcular total desde la BD para evitar manipulación de sesión
    db = get_db()
    try:
        total = 0
        validated_items = []
        for item in cart:
            p = db.execute(
                'SELECT id, nombre, precio FROM productos WHERE id = ? AND parent_id IS NULL',
                (item.get('id'),)
            ).fetchone()
            if p:
                qty = max(1, min(item.get('cantidad', 1), MAX_QTY))
                validated_items.append({'id': p['id'], 'nombre': p['nombre'], 'precio': p['precio'], 'cantidad': qty})
                total += p['precio'] * qty

        if not validated_items or total <= 0:
            flash('Error al procesar el carrito.', 'error')
            return redirect(url_for('cart.view_cart'))

        user = db.execute('SELECT * FROM usuarios WHERE id = ?', (session['user_id'],)).fetchone()
        if not user:
            flash('Usuario no encontrado.', 'error')
            return redirect(url_for('auth.login'))

        order_num = f"ORD-{int(time.time())}"

        db.execute(
            '''INSERT INTO pedidos (numero_orden, usuario_id, usuario_nombre, items, total, estado)
               VALUES (?, ?, ?, ?, ?, 'pendiente')''',
            (order_num, session['user_id'], user['nombre'], json.dumps(validated_items), total)
        )
        db.commit()

        msg_items = "\n".join(
            f"• {it['nombre']} x{it['cantidad']} = ${it['precio'] * it['cantidad']:,.0f}"
            for it in validated_items
        )
        msg = f"""Hola, me gustaría completar mi compra:

*Número de Orden:* {order_num}

*Items:*
{msg_items}

*Total:* ${total:,.0f}

Por favor confirmar disponibilidad y detalles de pago."""

        whatsapp_url = f"https://api.whatsapp.com/send?phone={WHATSAPP_PHONE}&text={quote(msg)}"
        session.pop('cart', None)

        return redirect(whatsapp_url)

    except Exception:
        flash('Error al procesar la compra.', 'error')
        return redirect(url_for('cart.view_cart'))
