# 📋 PRODUCTION DEPLOYMENT CHECKLIST

## ✅ Pasos Previos al Deploy

### 1. Seguridad
- [ ] Cambiar `SECRET_KEY` en `.env` a una cadena aleatoria larga (50+ caracteres)
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] Cambiar admin password por algo seguro
  ```bash
  python
  >>> from werkzeug.security import generate_password_hash
  >>> print(generate_password_hash('tu_nueva_passwd_aqui'))
  ```
- [ ] Actualizar contraseña en BD
- [ ] Verificar `debug=False` en app.py
- [ ] Usar HTTPS (SSL/TLS obligatorio)

### 2. Base de Datos
- [ ] Cambiar de SQLite a PostgreSQL/MySQL
  ```bash
  pip install psycopg2-binary  # PostgreSQL
  ```
- [ ] Hacer backup de base de datos actual
- [ ] Configurar usuario de BD con permisos limitados
- [ ] Habilitar SSL para conexión de BD

### 3. Dependencias
- [ ] Instalar producción:
  ```bash
  pip install -r requirements.txt
  pip install gunicorn python-dotenv
  ```

### 4. Variables de Entorno
- [ ] Crear archivo `.env` **NUNCA** en git
- [ ] Incluir: `SECRET_KEY`, `WHATSAPP_PHONE`, `DATABASE_URL`

### 5. Testing Final
- [ ] [ ] Probar login/registro
- [ ] Probar agregar productos
- [ ] Probar carrito y checkout
- [ ] Verificar pedidos en WhatsApp
- [ ] Test en navegadores diferentes
- [ ] Test de carga

---

## 🚀 Comandos de Desploy

```bash
# Clonar y configurar
git clone <repository>
cd artisan
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install gunicorn

# Configurar
cp .env.example .env
# Editar .env con valores reales

# Inicializar BD
python database_setup.py

# Ejecutar
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

---

## 📱 Con Docker (Recomendado)

```bash
docker build -t artisan .
docker run -p 5000:5000 --env-file .env artisan
```

---

**Estado**: ✅ Listo para production
