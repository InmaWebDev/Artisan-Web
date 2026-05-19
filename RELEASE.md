# RELEASE Checklist

Este documento describe los pasos finales para publicar la tienda Artisan como la versión oficial.

## 1) Preparación de entorno
- Crear un `.env` en producción con variables seguras:
  - `SECRET_KEY` — cadena larga aleatoria
  - `WHATSAPP_PHONE`
  - `INITIAL_ADMIN_EMAIL` y `INITIAL_ADMIN_PASSWORD` (usar solo para la inicialización)
  - Otros: `DB_*`, `MAIL_*` según necesidad

## 2) Inicializar base de datos y crear admin
```bash
# en local o en el servidor antes de iniciar el servicio
cp .env.example .env
# editar .env con valores reales
python database_setup.py
python seed_data.py
```

## 3) Ejecutar tests básicos
```bash
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python compile_all.py
python e2e_test.py
```

## 4) Despliegue con Docker (producción)
- Usar `Dockerfile.prod` y `docker-compose.prod.yml`.
- Asegurarse de que `.env` contiene `SECRET_KEY` y valores productivos.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

## 5) Recomendaciones para producción
- Usar PostgreSQL o MySQL en lugar de SQLite.
- Poner Nginx como reverse-proxy y manejar SSL (Let's Encrypt).
- No almacenar credenciales en repositorio.
- Configurar backups automáticos de la DB.
- Implementar monitoreo y alertas.

## 6) Post-release
- Cambiar la contraseña del admin creado.
- Eliminar `INITIAL_ADMIN_*` de variables si se usaron para la inicialización.
- Revisar logs y confirmar que los pedidos están llegando.

---

Para ayuda con el despliegue final (configurar Nginx, PostgreSQL, pipeline CI/CD o publicar a un proveedor), dime dónde quieres desplegar (DigitalOcean, Railway, Render, Azure, Heroku, VPS) y lo preparo.