from flask import Blueprint, request, render_template, redirect, url_for
from src.app.models.user import User
import uuid

user_bp = Blueprint('user', __name__)


@user_bp.route("/users")
def index():
    users = User.get_all()
    return render_template("users/lista_usuarios.html", users=users)


@user_bp.route("/users/formulario")
def formulario():
    return render_template("users/formulario_ejemplo.html")


@user_bp.route("/procesar", methods=["POST"])
def procesar():
    nombre = request.form["nombre"]
    edad = request.form.get("edad")
    email = request.form.get("email", f"{nombre.lower()}@example.com")
    
    # Crear y guardar el usuario
    user_id = str(uuid.uuid4())[:8]
    user = User(user_id=user_id, name=nombre, email=email, edad=edad)
    user.save()
    
    return redirect(url_for('user.index'))
