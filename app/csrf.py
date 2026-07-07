from flask import session, request, flash, redirect, url_for


def validate_csrf():
    if request.method != 'POST':
        return True
    token = request.form.get('csrf_token')
    if not token or token != session.get('csrf_token'):
        flash('Error de seguridad: formulario inválido. Intenta de nuevo.', 'error')
        return False
    return True


def csrf_required(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not validate_csrf():
            return redirect(request.referrer or url_for('shop.index'))
        return f(*args, **kwargs)
    return wrapper
