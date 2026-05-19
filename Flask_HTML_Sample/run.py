from flask import Flask, render_template
import os
from src.app.controllers.user_controller import user_bp

# Configurar las rutas de templates y static
template_dir = os.path.join(
    os.path.dirname(__file__), 'src', 'app', 'views', 'templates'
)
static_dir = os.path.join(os.path.dirname(__file__), 'src', 'app', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Registrar blueprints de los controladores
app.register_blueprint(user_bp)


@app.route("/")
def index():
    nombre = "Andres"
    return render_template("index.html", nombre=nombre)


if __name__ == "__main__":
    app.run(debug=True)
