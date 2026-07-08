---
topic_key: sdd/auditoria-produccion/explore
status: draft
---

# Auditoría de Producción (SDD Explore)

## 1. Status
**Status:** COMPLETE

## 2. Executive Summary
El proyecto se basa en una arquitectura Django + React (Vite) dockerizada (Nginx, Gunicorn/Daphne, Redis, MariaDB). A nivel estructural está listo para desplegarse en un VPS (como Oracle Cloud), pero requiere ciertos ajustes críticos de seguridad y configuración en el entorno de producción (especialmente en el manejo del archivo `.env.prod` y configuración SSL) para evitar vulnerabilidades graves.

## 3. Key Findings

### 3.1. Archivo `.env.prod`
- **Espacio en blanco problemático:** La variable `EMAIL_HOST_PASSWORD= "unof uhgi avhe gdpq"` tiene un espacio inicial. En bash/Docker, este espacio se incluye en la variable, lo que genera errores de autenticación con el servidor SMTP.
- **SECRET_KEY Insegura:** La clave es `"cambia-esta-clave-en-produccion-por-una-muy-larga-y-aleatoria"`. Aunque elude la validación de `django-insecure`, sigue siendo una clave de ejemplo predecible.
- **Gestión de Secretos:** El archivo contiene contraseñas reales (DB, Email). **ATENCIÓN:** Si este archivo está siendo trackeado por Git, las contraseñas están expuestas.

### 3.2. Seguridad (HTTPS y Cookies)
- **Sin SSL configurado:** `SECURE_SSL_REDIRECT=False`. El proyecto está pensado para servirse por HTTP nativo.
- **Cookies no seguras:** `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` dependerán de si hay HTTPS. Enviar cookies de sesión por HTTP (puerto 80) expone los tokens al robo de sesiones (Man-in-the-Middle).

### 3.3. Base de Datos
- Se está usando MariaDB a través de `docker-compose.yml` con persistencia en `db_data`. Esto es correcto y robusto para producción.
- Existen archivos de backup manuales en la raíz (`backup_aficionados_network.sql`, `backup_db.json`), pero no se observa un sistema de backups automáticos (ej. cron jobs en el VPS).

### 3.4. Archivos Estáticos y Multimedia
- Nginx está correctamente configurado para servir `/static/` y `/media/` usando alias y caché (`expires 30d;`). 
- Nginx también maneja de forma correcta el enrutamiento de WebSockets (`/ws/`) hacia Daphne/Django.
- IMPORTANTE: Para que Nginx sirva los assets de React (Vite), se debe ejecutar `npm run build` y luego `python manage.py collectstatic` dentro del contenedor `web`.

## 4. Risks
1. **Robo de cuentas:** Operar una red social en el año actual sin HTTPS es un riesgo gravísimo. Los passwords y sesiones viajan en texto plano.
2. **Error de SMTP recurrente:** El espacio accidental en `EMAIL_HOST_PASSWORD` va a romper los emails.
3. **Pérdida de datos:** Al carecer de backups automatizados, un fallo catastrófico en el disco de Oracle Cloud resultará en pérdida total de la BD.

## 5. Next Recommended
1. **Limpiar el `.env.prod`:** Eliminar espacios extra y generar un verdadero `SECRET_KEY`. (Asegurarse de añadir `.env.prod` al `.gitignore`).
2. **Configurar HTTPS/SSL:** Utilizar `Certbot` y Let's Encrypt en el Nginx del servidor de producción, y luego activar `SECURE_SSL_REDIRECT=True` y las cookies seguras en Django.
3. **Automatizar Backups:** Añadir un pequeño script de volcado de base de datos (`mysqldump`) en el host ejecutado por un `cron` diario.
4. **Despliegue:** Ejecutar `docker compose -f docker-compose.yml up -d --build` en el VPS y correr las migraciones/collectstatic.
