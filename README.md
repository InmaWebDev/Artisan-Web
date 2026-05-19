# 🎨 ARTISAN - Plataforma E-commerce

Sistema de tienda en línea con integración de WhatsApp para ventas.

## ✨ Características

✅ Autenticación y registro de usuarios
✅ Panel de administración para gestionar productos
✅ Carrito de compras con sesión
✅ Integración con WhatsApp para pedidos
✅ Gestión de categorías dinámicas
✅ Soporte para productos con variantes (subproductos)
✅ Múltiples imágenes por producto
✅ Contraseñas encriptadas

## 🚀 Instalación

### Requisitos Previos
- Python 3.8+
- pip
- SQLite3

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```bash
cd "c:\Users\57312\Documents\Artisan Web"
```

2. **Crear entorno virtual (Recomendado)**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus valores
```

5. **Inicializar base de datos**
```bash
python database_setup.py
```

6. **Ejecutar la aplicación**
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

### Dependencias de desarrollo
Si quieres ejecutar pruebas o scripts E2E, instala también el archivo de dependencias de desarrollo:
```bash
pip install -r dev-requirements.txt
```

La aplicación estará disponible en `http://localhost:5000`

### Opcional: Ejecutar con Docker
```bash
docker compose up --build
```

### Producción con Docker Compose y PostgreSQL
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

El archivo `docker-compose.prod.yml` levanta un servicio `db` con PostgreSQL y el servicio `web` con Gunicorn.

### Base de datos
El proyecto ahora soporta `DATABASE_URL` para PostgreSQL y cae a SQLite cuando no se define.

Ejemplo en `.env`:
```
DATABASE_URL=postgresql://artisan_user:PasswordSeguro@localhost:5432/artisan_db
```

### WSGI
Para despliegue en servidores se puede usar `wsgi.py` junto a Gunicorn:
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
```

## 👤 Credenciales de Administrador

No se incluye una contraseña por defecto por seguridad. Crea el administrador inicial antes de iniciar la aplicación estableciendo las variables de entorno en `.env` o `.env.docker`:

```
INITIAL_ADMIN_EMAIL=admin@artisan.com
INITIAL_ADMIN_PASSWORD=TuPasswordAdminSegura123!
```

Después ejecuta:

```
python database_setup.py
```

Y **cambia** la contraseña del admin inmediatamente después del primer acceso.

## 📋 Estructura del Proyecto

```
Artisan Web/
├── app.py                    # Aplicación principal
├── database_setup.py         # Inicialización de BD
├── database.db              # Base de datos SQLite
├── requirements.txt         # Dependencias Python
├── .env.example             # Ejemplo de variables de entorno
├── static/
│   ├── css/
│   │   └── style.css       # Estilos principales
│   ├── img/                # Imágenes de productos
│   └── js/                 # JavaScript (si aplica)
└── templates/
    ├── base.html           # Plantilla base
    ├── index.html          # Página de inicio
    ├── login.html          # Formulario de login
    ├── registro.html       # Formulario de registro
    ├── carrito.html        # Carrito de compras
    ├── admin.html          # Panel de administración
    └── ...                 # Otras plantillas
```

## 🔧 Configuración Importante

### WhatsApp
Cambiar el número de WhatsApp en `.env`:
```
WHATSAPP_PHONE=573123580705
```

### Seguridad
- Cambiar `SECRET_KEY` en `.env` (usar una cadena aleatoria larga)
- En producción, usar `debug=False`
- Usar HTTPS en todo momento

## 📦 API de Rutas

### Públicas (con login)
- `GET /` → Redirige a la tienda (`/index`)
- `POST /login` → Autenticar usuario
- `POST /registro` → Crear nueva cuenta
- `GET /index` → Tienda principal
- `GET /lineaproductos` → Listado de productos (con filtros)
- `GET /producto/<id>` → Detalle de producto
- `POST /logout` → Cerrar sesión

### Carrito
- `GET /carrito` → Ver carrito
- `GET /carrito/add/<id>?cantidad=N` → Agregar al carrito
- `GET /carrito/remove/<id>` → Remover del carrito
- `GET /carrito/update/<id>?cantidad=N` → Actualizar cantidad
- `GET /carrito/clear` → Vaciar carrito
- `POST /carrito/checkout` → Procesar compra (→ WhatsApp)

### Admin (solo administrador)
- `GET /admin` → Panel de administración
- `POST /admin/add_prod` → Agregar producto
- `POST /admin/cat/add` → Crear categoría
- `GET /admin/cat/del/<id>` → Eliminar categoría
- `GET /admin/prod/del/<id>` → Eliminar producto
- `GET /admin/prod/edit/<id>` → Editar producto
- `POST /admin/prod/edit/<id>` → Guardar cambios

## 🔐 Seguridad

- ✅ Contraseñas encriptadas con werkzeug.security
- ✅ Validación de entrada en todos los formularios
- ✅ Límites en cantidad de artículos (máx. 1000)
- ✅ Validación de precios (deben ser positivos)
- ✅ Protección de rutas administrativas
- ⚠️ Agregar HTTPS en producción
- ⚠️ Usar base de datos externa en producción (no SQLite)

## 🔄 Flujo de Compra

1. Usuario se registra o inicia sesión
2. Navega por productos
3. Agrega productos al carrito
4. Revisa el carrito
5. Hace click en "COMPRAR POR WHATSAPP"
6. Se registra el pedido en la BD
7. Se abre WhatsApp con mensaje preformulado
8. Usuario y vendedor pactan detalles de pago
9. Vendedor confirma la orden en el panel admin

## 📊 Información de Pedidos

Todos los pedidos se guardan con:
- Número de orden único (ORD-timestamp)
- Nombre del cliente
- Lista de items en JSON
- Total
- Estado (pendiente/confirmado/cancelado)
- Fecha/Hora de creación

## 🐛 Solución de Problemas

### Base de datos corrupta
```bash
rm database.db
python database_setup.py
```

### Contraseñas hashed incorrectamente
```bash
# Reimportar para regenerar database
rm database.db
python database_setup.py
python app.py
```

### Puerto en uso
Cambiar puerto en app.py línea final:
```python
app.run(host='0.0.0.0', port=8000, debug=False)
```

## 📱 Requisitos para Producción

- [ ] Cambiar `debug=False` en app.py
- [ ] Usar variables de entorno (`python-dotenv`)
- [ ] Usar HTTPS (certificado SSL)
- [ ] Usar base de datos externa (PostgreSQL, MySQL)
- [ ] Usar servidor WSGI (Gunicorn, uWSGI)
- [ ] Configurar CORS si es necesario
- [ ] Agregar rate limiting
- [ ] Configurar backups automáticos
- [ ] Usar variables de entorno para credenciales

## 📞 WhatsApp Business

Para optimizar el flujo:
1. Crear cuenta WhatsApp Business
2. Usar API oficial de WhatsApp Cloud
3. Automatizar respuestas
4. Guardar historial de conversaciones

## 📝 Licencia

Este proyecto es privado.

## 👨‍💻 Desarrollador

Artisan Web 2026

---

**¿Necesitas ayuda?** Contacta al equipo de desarrollo.
