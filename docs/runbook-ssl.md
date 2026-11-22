# Runbook de Producción: Zero-Downtime SSL/TLS con Let's Encrypt, Certbot y Nginx

**Versión:** 1.0.0  
**Fecha de Publicación:** 2026-11-22  
**Entorno de Producción:** Oracle Cloud Infrastructure (`141.148.227.48`)  
**Stack:** Django 4.2 / Channels / Daphne, Nginx 1.25 Alpine, Certbot, Docker Compose  

---

## 1. Visión General y Arquitectura

Este runbook describe el procedimiento operativo estándar para aprovisionar y activar certificados SSL/TLS emitidos por **Let's Encrypt** en la plataforma **Hubs & Clicks**, garantizando **cero tiempo de inactividad (Zero-Downtime)** durante la transición de HTTP a HTTPS.

### ¿Por qué el enfoque Webroot en lugar de Standalone?
- **Modo Standalone (Anti-patrón en producción):** Requiere detener Nginx para que Certbot escuche directamente en el puerto 80, provocando caída de servicio y errores 502/conexión rechazada a los usuarios conectados.
- **Modo Webroot (Arquitectura adoptada):** Nginx permanece en ejecución continua sirviendo peticiones web normales. Certbot deposita el archivo de desafío criptográfico en el volumen compartido `/var/www/certbot`, y Nginx responde a Let's Encrypt en la ruta `/.well-known/acme-challenge/`. Una vez emitido el certificado, Nginx se recarga en caliente (`nginx -s reload`) en milisegundos sin cerrar sockets ni conexiones WebSocket activas.

```
                    Internet (Cliente / Let's Encrypt CA)
                                     │
                             (Puerto 80 HTTP)
                                     │
                        ┌────────────▼────────────┐
                        │   Nginx (Contenedor)     │
                        └────────────┬────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
     Ruta normal / o /api/                  /.well-known/acme-challenge/
                 │                                       │
                 ▼                                       ▼
       [Daphne / Django Web]                [Volumen certbot_www]
                                                         ▲
                                                         │ (Escribe token)
                                            [Certbot Contenedor]
```

---

## 2. Prerrequisitos

1. **Servidor en Ejecución:** Docker y Docker Compose activos en `141.148.227.48`.
2. **Dominio Comprado / Gestionado:** Un dominio propio (ejemplo: `hubsandclicks.com` o similar) registrado en Namecheap, GoDaddy, Cloudflare, DonDominio u otro registrador.
3. **Herramienta `envsubst` instalada en el host:** Generalmente disponible mediante `gettext-base` (`sudo apt-get install -y gettext-base` en Debian/Ubuntu).

---

## 3. Procedimiento Operativo Paso a Paso

### Paso 1: Configuración de Registros DNS

Antes de solicitar cualquier certificado a Let's Encrypt, los registros DNS deben resolver inequívocamente hacia la IP pública de producción.

1. Iniciar sesión en el panel del registrador o proveedor DNS (ej. Cloudflare, Namecheap).
2. Crear los siguientes registros **Tipo A**:
   - **Nombre / Host:** `@` (o la raíz del dominio)  
     **Tipo:** `A`  
     **Valor / Destino:** `141.148.227.48`  
     **TTL:** Auto o 300 segundos
   - **Nombre / Host:** `www`  
     **Tipo:** `A`  
     **Valor / Destino:** `141.148.227.48`  
     **TTL:** Auto o 300 segundos

> [!WARNING]
> **Si usas Cloudflare:** Configura el proxy en modo **"DNS Only" (Nube Gris)** durante la emisión inicial. Si la nube naranja está activa, Let's Encrypt intentará validar contra los servidores CDN de Cloudflare y la validación HTTP-01 fallará si no está preconfigurado. Una vez obtenido el certificado, puedes activar la nube naranja con modo SSL "Full (Strict)".

3. **Verificación de Propagación DNS:**
   Ejecutar desde una terminal externa o desde el propio servidor:
   ```bash
   dig +short midominio.com
   dig +short www.midominio.com
   ```
   *Ambos comandos deben retornar `141.148.227.48` antes de avanzar.*

---

### Paso 2: Preparar Volúmenes y Obtener Certificados con Certbot Webroot

Nginx ya cuenta con la directiva `location /.well-known/acme-challenge/` apuntando a `/var/www/certbot`.

1. **Asegurar que los volúmenes de Certbot estén vinculados en Nginx:**
   Si Nginx no ha sido recreado con los volúmenes `certbot_www` y `certbot_conf`:
   ```bash
   docker compose up -d nginx
   ```

2. **Solicitar el Certificado SSL:**
   Reemplazar `midominio.com` y `tu-email@ejemplo.com` por los valores reales:
   ```bash
   docker compose run --rm certbot certonly \
     --webroot \
     --webroot-path=/var/www/certbot \
     -d midominio.com \
     -d www.midominio.com \
     --email tu-email@ejemplo.com \
     --agree-tos \
     --no-eff-email
   ```

3. **Verificación del Éxito:**
   Let's Encrypt imprimirá un mensaje confirmando la generación de:
   - Certificate: `/etc/letsencrypt/live/midominio.com/fullchain.pem`
   - Key: `/etc/letsencrypt/live/midominio.com/privkey.pem`

   Verificar que Nginx tiene visibilidad de los archivos:
   ```bash
   docker compose exec nginx ls -la /etc/letsencrypt/live/midominio.com/
   ```

---

### Paso 3: Aplicar la Plantilla SSL en Nginx y Recargar en Caliente

1. **Generar la configuración activa de Nginx desde la plantilla:**
   Definir la variable de entorno `DOMAIN` y renderizar `production-ssl.conf.template`:
   ```bash
   export DOMAIN="midominio.com"
   envsubst '${DOMAIN}' < nginx/production-ssl.conf.template > nginx/default.conf
   ```

   > [!NOTE]
   > El uso explícito de `'${DOMAIN}'` como argumento en `envsubst` es **fundamental** para que únicamente se sustituya la variable `${DOMAIN}` y se preserven intactas las variables nativas de Nginx como `$host`, `$request_uri`, `$binary_remote_addr`, etc.

2. **Comprobar la Sintaxis de Nginx (Pre-flight check):**
   ```bash
   docker compose exec nginx nginx -t
   ```
   *Salida esperada:*
   ```text
   nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
   nginx: configuration file /etc/nginx/nginx.conf test is successful
   ```

3. **Recargar Nginx sin Caída de Servicio (Zero-Downtime Reload):**
   ```bash
   docker compose exec nginx nginx -s reload
   ```

4. **Comprobación de Redirección y Certificado:**
   ```bash
   # Comprobar redirección 301 de HTTP a HTTPS
   curl -I http://midominio.com

   # Comprobar respuesta 200 en HTTPS con certificado válido
   curl -Iv https://midominio.com
   ```

---

### Paso 4: Activación de Flags de Seguridad Estricta en Django (`.env.prod`)

Con HTTPS operativo a nivel de servidor perimetral (Nginx), se deben blindar las cookies de sesión y autenticación en Django.

1. **Editar `.env.prod`:**
   ```bash
   nano .env.prod
   ```

2. **Actualizar y asegurar las siguientes variables:**
   ```env
   # Permitir el dominio nuevo y la IP
   ALLOWED_HOSTS=141.148.227.48,localhost,127.0.0.1,midominio.com,www.midominio.com

   # Confianza CSRF para solicitudes HTTPS
   CSRF_TRUSTED_ORIGINS=https://midominio.com,https://www.midominio.com,http://141.148.227.48

   # --- SEGURIDAD HTTPS ---
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   SECURE_HSTS_SECONDS=31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS=True
   SECURE_HSTS_PRELOAD=True
   ```

3. **Reiniciar el Contenedor Web/Django:**
   ```bash
   docker compose restart web
   ```

   *(Opcional: Si se utilizan workers Celery para tareas con URLs canónicas en correos)*:
   ```bash
   docker compose restart celery_worker celery_beat
   ```

---

### Paso 5: Automatización de Renovaciones

Los certificados de Let's Encrypt expiran a los 90 días. Se configuran dos mecanismos de renovación garantizada:

#### Opción A: Contenedor Daemon de Certbot (Recomendado)
El servicio `certbot` en `docker-compose.yml` ya está diseñado para ejecutar `certbot renew` cada 12 horas.
Para iniciarlo en background permanente:
```bash
docker compose up -d certbot
```

Para asegurar que Nginx recargue la configuración cuando haya una renovación efectiva, se puede añadir un deploy hook o utilizar un cron en el servidor host.

#### Opción B: Cron Job en el Servidor Host (Alta Fiabilidad)
Añadir una entrada al crontab del sistema (`crontab -e`):
```cron
0 3 * * 1 cd /home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2 && docker compose run --rm certbot renew --quiet && docker compose exec nginx nginx -s reload
```
*Este cron se ejecuta todos los lunes a las 03:00 AM, renueva certificados si restan menos de 30 días para su expiración y recarga Nginx en caliente.*

#### Prueba de Renovación Simulada (Dry-Run):
```bash
docker compose run --rm certbot renew --dry-run
```
*Debe retornar `Congratulations, all simulated renewals succeeded`.*

---

## 4. Plan de Rollback / Contingencia Inmediata

Si ocurre algún inconveniente crítico (ejemplo: error en DNS, expiración accidental o problemas con certificados):

1. **Restaurar Nginx a modo HTTP:**
   ```bash
   # Revertir a la configuración base que escucha en HTTP 80/8000
   git checkout nginx/default.conf
   docker compose exec nginx nginx -s reload
   ```

2. **Revertir Flags en `.env.prod`:**
   ```env
   SECURE_SSL_REDIRECT=False
   SESSION_COOKIE_SECURE=False
   CSRF_COOKIE_SECURE=False
   ```

3. **Reiniciar Django:**
   ```bash
   docker compose restart web
   ```

El sistema volverá a operar de inmediato bajo HTTP en `http://141.148.227.48` sin interrupciones adicionales.
