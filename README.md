# 🚀 Hubs&Clicks - Red social privada para terapeutas naturales

Hubs&Clicks es una plataforma web de carácter privado, diseñada para conectar a terapeutas y profesionales del bienestar a través de sus terapias, permitiéndoles organizar eventos presenciales y online, compartir conocimientos en una Biblioteca de Casos y estudios clínicos, intercambiar y comercializar recursos en un Mercadillo especializado, y comunicarse en tiempo real mediante un sistema de mensajería seguro, moderno y con una identidad corporativa unificada.

---

## 🛠️ Arquitectura y Capacidades de Producción

### 1. Gestión de Eventos 360º y Recordatorios Automáticos (Celery Beat)
- **Creación y Edición Integral:** Planes detallando ubicación física o streaming online, fecha, terapia, nivel de experiencia y límite de aforo físico.
- **Sincronización Automática con Chat (Eventos Online):** Los eventos online generan automáticamente una sala de chat grupal privada. Los asistentes se unen en tiempo real vía Django Signals para coordinar la sesión.
- **Recordatorios Automáticos 24h con Idempotencia Multinivel:**
  - Servicio programado independiente **Celery Beat** ejecutándose a diario a las 08:00 AM (`crontab(hour=8, minute=0)`), despachando `posts.tasks.send_event_reminders_task`.
  - **Garantía Zero-Duplicates:** Control de idempotencia a nivel base de datos (`reminder_sent`, `reminder_sent_at` e índice compuesto en `EventAttendance`), deduplicación en el modelo `Notification` y transaccionalidad atómica (`transaction.atomic()`).
  - Despacho de emails HTML corporativos con detalles específicos según la modalidad (enlace de streaming para eventos online o mapa y dirección para eventos presenciales).
- **Sistema de Duplicado y Cancelación:** Clonación de eventos pasados con un clic y protocolo seguro de cancelación con alertas automáticas a todos los participantes.

### 2. Notificaciones Centralizadas (`NotificationDispatcher`)
- **Arquitectura de Despacho Desacoplado:** Motor centralizado en `notifications/services.py` que coordina notificaciones en-app (campana con badges y recarga asíncrona HTMX) y correos HTML corporativos.
- **Encolado Asíncrono Resiliente (Celery + Redis):** Tarea `send_email_task` desacoplada del ciclo de vida HTTP con reintentos exponenciales con jitter (hasta 5 reintentos) y contingencia defensiva in-process mediante `ThreadPoolExecutor` ante microcortes.
- **Cobertura Completa del Negocio:** Alertas instantáneas para likes, comentarios en posts, nuevos seguidores, confirmación de asistencia a eventos, recordatorios 24h, solicitudes de acceso a grupos de chat, reviews entre terapeutas, medallas de gamificación y comentarios/valoraciones en la biblioteca clínica.

### 3. Mensajería en Tiempo Real y Frontend React 100% Strict TypeScript 💬
- **Salas Privadas y Grupales:** Chats 1 a 1 y grupos temáticos sobre WebSockets ASGI blindados con `AllowedHostsOriginValidator` para mitigar ataques CSWSH.
- **Frontend Moderno con Strict TypeScript:**
  - Aplicación React 19 embebida vía Vite 8, migrada íntegramente a **TypeScript estricto** (`.tsx`/`.ts`).
  - Verificación formal de tipos mediante script `npm run type-check` (`tsc --noEmit`) con 0 advertencias y 0 errores.
  - Arquitectura **Container - Presentational (Smart vs. Dumb)**: Contenedor `MessageArea.tsx` coordinando subcomponentes especializados (`MessageTimeline`, `MessageInput`, `AttachmentPreview`, `GroupParticipants`, `GroupPendingRequests`, `GroupAddMember`).
  - **Capa Anti-Corrupción (ACL):** Cliente HTTP centralizado (`httpClient.ts`) con intercepción y sanitización automática del token CSRF, desacoplando los componentes de llamadas de red crudas mediante `chat.service.ts` y contratos formales en `chat.types.ts`.
- **Privacidad de Archivos Adjuntos (Anti-IDOR & Magic Bytes):**
  - **Validación Binaria Estricta:** Comprobación de firmas reales (*magic bytes*) para JPG, PNG, GIF, WEBP y PDF, y sanitización de metadatos EXIF sensibles mediante Pillow.
  - **Despacho Protegido (`X-Accel-Redirect`):** Acceso directo a `/media/chat_attachments/` bloqueado perimetralmente en Nginx. La descarga se gestiona exclusivamente a través de `ProtectedAttachmentDownloadView` tras verificar que el usuario pertenece activamente a la conversación.
  - **Presentación Enriquecida de Documentos:** Nombres de archivo reales limpios de sufijos aleatorios internos (`attachment_name`), previsualizaciones tematizadas con iconos de Lucide (badges rojos para PDF, verde para hojas de cálculo, azul para documentos, ámbar para comprimidos, violeta para código) y descarga directa con 1 clic (`?download=1`).
- **Control Total:** Opciones de "Eliminar para todos" (borrado físico del mensaje y destrucción del archivo adjunto en disco) y "Eliminar para mí" (borrado lógico local).

### 4. Seguridad Perimetral y OWASP Hardening 🛡️
- **Saneamiento Anti-XSS (Doble Barrera):** Motor de sanitización con `nh3` en métodos `save()` de modelos (`Article`, `Event`, `Profile`) con listas blancas rigurosas de etiquetas HTML seguras, y filtro de plantilla personalizado `|sanitize_html`.
- **Rate Limiting Perimetral:** Reglas de limitación de tasa en Nginx (`limit_req_zone`) sobre endpoints sensibles (`/login/`, `/contact/`) para prevenir ataques de fuerza bruta y DoS.
- **Zero-Downtime SSL/TLS Readiness:**
  - Infraestructura preparada para aprovisionar certificados Let's Encrypt mediante el protocolo **ACME Webroot** (`/.well-known/acme-challenge/`), compartiendo volúmenes entre Nginx y Certbot en Docker Compose.
  - Cero tiempo de inactividad: Nginx se mantiene en ejecución atendiendo tráfico web y sockets, y se recarga en caliente (`nginx -s reload`) en milisegundos tras la emisión o renovación.
  - Plantilla declarativa `nginx/production-ssl.conf.template` lista para despliegue inmediato con `envsubst '${DOMAIN}'`.
  - Guía operativa paso a paso disponible en el [Runbook de Producción SSL](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/docs/runbook-ssl.md).
- **Control de Secretos:** `.gitignore` y `.dockerignore` exhaustivos para garantizar que ningún archivo `.env*`, volcado de base de datos ni credencial sensible se incluya en el repositorio ni en las imágenes Docker.

### 5. Directorio de Terapeutas, Mercadillo y Biblioteca Clínica
- **Comunidad de Profesionales:** Exploración fluida mediante scroll infinito (HTMX) y búsqueda multi-campo. Privacidad de contacto (teléfono, email, dirección) reservada a miembros registrados.
- **Canal Oficial "Ágora" (`slug="agora"`):** Categoría institucional reservada exclusivamente para directiva (`is_staff`), asignada automáticamente a todos los usuarios registrados y fijada prioritariamente al inicio de los feeds de la plataforma.
- **Biblioteca de Casos Clínicos y Artículos:** Publicaciones de divulgación técnica con editor enriquecido TinyMCE, extracción y decodificación universal de entidades HTML (`plain_text_summary`), y sistema de comentarios y valoraciones integrado con el `NotificationDispatcher`.
- **Mercadillo de Profesionales:** Directorio de compra, venta, alquiler e intercambio de material y espacios terapéuticos, con enlaces directos a salas de chat privadas y sistema de valoraciones (reviews de 1 a 5 estrellas).

### 6. Sistema de Temas Unificado (Light & Dark) y Contraste Semántico (WCAG AA) 🎨
- **Jerarquía Tonal Semántica Bootstrap 5.3:** Tokens semánticos estandarizados (`--bs-body-bg`, `--bs-card-bg`, `--bs-tertiary-bg`, `--bs-body-color`, `--bs-border-color`) eliminando clases rígidas como `bg-white`, `bg-light` y `text-dark` en más de 35 templates Django.
- **Sincronización Reactiva Multi-Capa en Microfrontend:** Hook `useHostTheme` en React sincronizado en tiempo real con el selector del host Django mediante CustomEvent (`themeChanged`) y `MutationObserver` defensivo.
- **Arquitectura de Cascada CSS Invertida y Blindaje de Terceros:**
  - Carga prioritaria de librerías CDN en `{% block extra_css %}` antes de `style.css` en `layout.html`, asegurando la precedencia de diseño de la aplicación.
  - Blindaje con selector calificado `[data-bs-theme="dark"]` y variables semánticas para componentes complejos como TomSelect (`.ts-control`, `.ts-dropdown`) y editores WYSIWYG TinyMCE (`oxide-dark`), garantizando contraste perfecto y legibilidad sin fondos blancos residuales.

---

## 💻 Stack Tecnológico

| Capa | Tecnologías | Propósito |
| :--- | :--- | :--- |
| **Backend Core** | Django 6.0, Python 3.12 | Arquitectura MVC, ORM, autenticación por email, administración y API REST. |
| **Tiempo Real (ASGI)** | Django Channels 4.2+, Daphne | Servidor ASGI para WebSockets de mensajería con validación de origen. |
| **Base de Datos** | MariaDB 10.11 / SQLite 3 | MariaDB en producción con charset `utf8mb4`; SQLite para desarrollo local y tests rápidos en memoria. |
| **Broker & Caché** | Redis 7 Alpine | Canal de transporte para Django Channels y broker/backend de Celery. |
| **Tareas Asíncronas** | Celery 5.7+ Worker | Encolado de emails corporativos y notificaciones pesadas con reintentos exponenciales. |
| **Programador Periódico** | Celery Beat | Ejecución programada de recordatorios de eventos 24h a las 08:00 AM. |
| **Proxy & Servidor Web** | Nginx 1.25 Alpine | Reverse proxy, terminación SSL/TLS, Rate Limiting, CSP Sandbox y `X-Accel-Redirect`. |
| **Certificados SSL** | Certbot (Let's Encrypt) | Emisión y renovación automática de certificados SSL/TLS con Zero-Downtime Webroot. |
| **Frontend Chat** | React 19, TypeScript 5+, Vite 8 | Módulo de chat en tiempo real 100% tipado, empaquetado como bundle optimizado. |
| **Frontend Web** | Bootstrap 5.3, HTMX, Vanilla JS | Renderizado server-side accesible, scroll infinito y modo oscuro armonizado. |
| **Seguridad & Media** | `nh3`, Pillow 10+ | Sanitización estricta de HTML y validación binaria de metadatos EXIF. |
| **Calidad & Testing** | Django Test Runner, TypeScript Compiler | 126 tests unitarios/integración en ~6.1s (100% GREEN) + `tsc --noEmit`. |

---

## 🐳 Servicios en Docker Compose

La infraestructura de producción está completamente modularizada en [docker-compose.yml](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/docker-compose.yml):

```yaml
services:
  web:           # Django 6.0 + Channels Daphne ASGI (puerto interno 8000)
  db:            # MariaDB 10.11 con almacenamiento persistente en 'db_data'
  redis:         # Redis 7 Alpine para Channels y Celery
  celery_worker: # Worker Celery para tareas de email y notificaciones
  celery_beat:   # Programador Celery Beat para recordatorios de eventos 24h
  nginx:         # Proxy inverso Nginx 1.25 (puertos 80, 8000, 443) con X-Accel-Redirect
  certbot:       # Cliente ACME para emisión y renovación automática cada 12h
```

---

## ⚙️ Instalación y Entorno Local de Desarrollo

### Requisitos Previos
- Python 3.12+
- Node.js 20+ y npm
- Redis Server (local o vía Docker)
- Tmux (opcional, para ejecución automatizada en paneles)

### Paso 1: Clonar el Repositorio y Configurar Entorno Virtual
```bash
git clone https://github.com/tu-usuario/aficionados_network.git
cd aficionados_network

python3 -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
pip install -r requirements.txt
```

### Paso 2: Configurar Variables de Entorno
Copia la plantilla de variables de entorno y ajusta tus credenciales locales:
```bash
cp .env.example .env
```

Para desarrollo local rápido con SQLite, asegúrate de tener:
```env
DEBUG=True
SECRET_KEY=django-insecure-entorno-de-desarrollo-local
DB_ENGINE=sqlite
```

### Paso 3: Migraciones y Superusuario
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Paso 4: Levantar el Entorno de Desarrollo

#### Opción A: Entorno Automatizado con Tmux (Recomendado)
El proyecto incluye el script [start_dev.sh](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/start_dev.sh) que levanta en paneles sincronizados (Ventana 0 - "Servicios"):
1. Panel 1: Servidor Django ASGI con Daphne (`python manage.py runserver`)
2. Panel 2: Vite Dev Server para el Chat React (`cd frontend && npm run dev`)
3. Panel 3: Celery Worker para tareas asíncronas y emails (`celery -A aficionados_network worker -l info`)
4. Panel 4: Redis Server / Monitor (`redis-server` / `redis-cli monitor`)

Además, crea una **Ventana 1 ("Terminal")** independiente con el entorno virtual activo para comandos interactivos.

Para iniciar:
```bash
chmod +x start_dev.sh stop_dev.sh
./start_dev.sh
```

Para detener todo el entorno de forma limpia (liberando procesos, bases de datos y puertos):
```bash
./stop_dev.sh
```

#### Opción B: Ejecución Manual
En terminales separadas:
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Vite (Frontend Chat)
cd frontend && npm install && npm run dev

# Terminal 3: Celery Worker (Opcional en desarrollo)
celery -A aficionados_network worker -l info

# Terminal 4: Django Backend
python manage.py runserver
```
La aplicación estará disponible en `http://127.0.0.1:8000`.

---

## 🧪 Testing y Calidad de Código

El proyecto cuenta con una batería de pruebas rigurosa que cubre modelos, servicios de notificaciones, APIs REST, Channels WebSockets, transacciones de base de datos y tipado estático:

### 1. Tests Unitarios y de Integración (Backend)
Configurados con aceleración en memoria (`MD5PasswordHasher`, `InMemoryChannelLayer`, `CELERY_TASK_ALWAYS_EAGER`):
```bash
# Ejecución con el entorno virtual activo (126 tests)
./env/bin/python manage.py test
```
*Salida esperada:*
```text
Ran 126 tests in ~6.1s
OK
```

### 2. Verificación de Tipos TypeScript (Frontend)
```bash
cd frontend
npm run type-check
```
*Salida esperada:*
```text
> tsc --noEmit
(0 errores, compilación estricta aprobada)
```

### 3. Compilación de Producción Frontend (Vite)
```bash
cd frontend
npm run build
```

---

## 🚢 Despliegue en Producción y SSL Zero-Downtime

Para desplegar en servidores de producción (ej. Oracle Cloud, Ubuntu Server):

1. **Configurar `.env.prod`:**
   Asegurar las credenciales de MariaDB, clave secreta de producción, credenciales de Gmail SMTP (`EMAIL_HOST_PASSWORD`) y hosts permitidos.

2. **Construir y Levantar Contenedores:**
   ```bash
   docker compose up -d --build
   ```

3. **Ejecutar Migraciones y Recolección de Estáticos:**
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py collectstatic --noinput
   ```

4. **Aprovisionamiento SSL/TLS (Zero-Downtime):**
   Para asociar un dominio oficial y obtener certificados HTTPS gratuitos de Let's Encrypt sin detener la aplicación ni cerrar sockets activos, consulta el:
   📖 **[Runbook de Producción SSL/TLS (docs/runbook-ssl.md)](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/docs/runbook-ssl.md)**.

---

## 🏆 Roadmap de Madurez Técnica (100% Completado)

- [x] **Arquitectura Asíncrona Resiliente:** Celery 5.7+ con Redis y reintentos exponenciales para emails transaccionales.
- [x] **Celery Beat Scheduler:** Recordatorios automáticos de eventos 24h a las 08:00 AM con estricta idempotencia multinivel.
- [x] **Despachador Centralizado (`NotificationDispatcher`):** Servicio orquestador para avisos in-app y alertas por correo en todas las interacciones de negocio.
- [x] **Frontend 100% Strict TypeScript:** React 19 + TypeScript con tipado riguroso, contratos formales y Capa Anti-Corrupción (`httpClient.ts`).
- [x] **Seguridad de Archivos y Anti-IDOR:** Bloqueo de acceso directo en Nginx y descarga validada con `X-Accel-Redirect`, comprobación binaria de magic bytes y eliminación de metadatos EXIF con Pillow.
- [x] **Hardening OWASP:** Saneamiento Stored XSS con `nh3`, mitigación de CSWSH en ASGI, Rate Limiting en Nginx y purga de secretos.
- [x] **Zero-Downtime SSL Readiness:** Nginx configurado con ACME challenge webroot, servicio Certbot en Docker Compose y plantilla de producción lista.
- [x] **Suite de Tests Exhaustiva:** 126 tests automatizados ejecutados en ~6.1s con 100% de éxito.

---

**Hubs&Clicks** - *"Conectando personas y bienestar a través de la experiencia compartida."*
