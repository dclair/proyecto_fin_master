---
topic_key: sdd/auditoria-produccion/explore
status: COMPLETED
date: 2026-11-17
auditor: Senior Software Architect & GDE
change: auditoria-produccion
---

# Auditoría de Arquitectura, Seguridad & Preparación para Producción

## 1. Status
**Status:** COMPLETED — RECHAZADO PARA PRODUCCIÓN (Veredicto: **NO APTO / CONDICIÓN CRÍTICA**)

---

## 2. Executive Summary

Bancá un segundo y mirémonos a la cara: si mandás esto a producción hoy a una máquina expuesta en Oracle Cloud, **en menos de 48 horas te voltean la base de datos, te clonan las credenciales de administración, te secuestran el SMTP para mandar spam a escala masiva y te inyectan código malicioso a través de XSS almacenado**. 

No te voy a mentir ni te voy a dorar la píldora: el proyecto tiene intenciones funcionales copadas y el ecosistema híbrido (Django + Channels + React integrado vía Vite) demuestra esfuerzo. Pero la ingeniería de software no es un rejunte de tutoriales de YouTube donde copiás y pegás código hasta que "más o menos anda". 

Acá somos Tony Stark diseñando el reactor arc; el código es nuestra armadura. Y ahora mismo, esta armadura tiene remaches de cartón, cables pelados tocando nafta y la visera abierta de par en par:
1. **Brechas de Seguridad Alarmantes:** Volcados completos de base de datos de producción con hashes de contraseñas de usuarios y administradores (`auth_user`) comiteados directamente en Git; `.dockerignore` inexistente (lo que copia secretos, `.env`, `.git` y volcados SQL adentro de la imagen Docker final); Stored XSS en al menos tres pantallas clave mediante el filtro `|safe` sin saneamiento; Cross-Site WebSocket Hijacking (CSWSH) por falta de validación de origen en ASGI; relay abierto de correo en el formulario de contacto; cambios de estado destructivos vía `GET` (CSRF); e inexistencia absoluta de TLS/HTTPS en Nginx y Django.
2. **Violación Total de SOLID y de la Filosofía Gentleman (Alan Buscaglia):** En el frontend nos vendieron una arquitectura moderna, pero **no hay una sola línea de TypeScript**. Todo es JavaScript puro (`.jsx`/`.js`), sin modelos de dominio, sin adaptadores anti-corrupción, con componentes "Dios" de más de 750 líneas (`MessageArea.jsx`) que violan el principio de responsabilidad única (SRP), acoplamiento directo a `axios` sin capas de abstracción (violando DIP) y parseos artesanales repetidos de `document.cookie` en cinco componentes distintos.
3. **Deuda Técnica y Desempeño Catastrófico:** Señales Django que ejecutan bucles N+1 demoledores ante cada "like" para recalcular medallas en tiempo real de forma síncrona, envíos de correo SMTP bloqueantes dentro del ciclo de vida de la petición HTTP sin colas de tareas (Celery/RQ) y una cobertura de tests inexistente en tres módulos completos del backend y un rotundo 0% en el frontend.

**Veredicto:** El despliegue a producción queda **VETADO** hasta sanear los vectores de ataque críticos y refactorizar las capas estructurales.

---

## 3. Key Findings

```
                                  MAPA DE VULNERABILIDADES & DEUDA
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [CLIENTE EXTERNO]                                                                                      │
│   │                                                                                                    │
│   ├── (HTTP Sin TLS :80) ──> [NGINX: default.conf]                                                     │
│   │                            │  (Sin HSTS, Sin CSP, Sin Rate-Limit, Alias /media/ expuesto a XSS)    │
│   │                            ▼                                                                       │
│   ├── (WS Sin Origin Check) ─> [DAPHNE / CHANNELS: asgi.py] ──> Cross-Site WebSocket Hijacking         │
│   │                                                                                                    │
│   └── (HTTP Requests) ───────> [DJANGO CORE: settings.py & views]                                      │
│                                  │                                                                     │
│                                  ├──> ContactFormView: Relay Abierto de SPAM vía CC síncrono           │
│                                  ├──> posts/views: duplicate_event, attendance por GET (CSRF)          │
│                                  ├──> marketplace/views: Open Redirect sin validar next_url            │
│                                  ├──> Templates: bio|safe, event.desc|safe, article|safe (Stored XSS)  │
│                                  ├──> Signals: Bucle N+1 síncrono al likear (DDoS accidental a MariaDB)│
│                                  └──> Docker build: COPY . . sin .dockerignore (Fuga de Secretos/Git)  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### EJE 1: Seguridad, Control de Acceso e Infraestructura HTTP

#### 1.1. Fuga Masiva de Credenciales y Base de Datos en el Repositorio Git (CRÍTICO)
- **Archivos Afectados:**
  - [backup_aficionados_network.sql](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/backup_aficionados_network.sql#L387-L392)
  - [backup_db.json](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/backup_db.json#L451)
  - [cookies.txt](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/cookies.txt#L1-L5)
  - [chat_debug.log](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/chat_debug.log#L1-L30)
- **Evidencia Técnica:**
  En `backup_aficionados_network.sql`, líneas 387-392, se encuentran commiteados los volcados reales de la tabla `auth_user`, conteniendo usuarios (`root`, `admin`, `Juan`, `pepe`), direcciones de correo reales y los hashes PBKDF2 correspondientes:
  ```sql
  INSERT INTO `auth_user` VALUES
  (1,'pbkdf2_sha256$1200000$RDM3M6P6QeqfqnWFRVHTEs$nGvvgw80sH4PYbmWqqnw0kUqfYMFwhK03Fz20OX4QnA=','2026-06-18 10:23:45.771637',1,'root','','','0y1informatica@gmail.com',1,1,'2026-01-17 18:01:41.000000');
  ```
  Asimismo, `cookies.txt` expone tokens CSRF y `chat_debug.log` expone detalles de sesiones de depuración internas.
- **Impacto:** Cualquier persona o agente con acceso de lectura al repositorio tiene acceso inmediato a la base de datos de usuarios, sus correos y mensajes privados.

#### 1.2. Inexistencia de `.dockerignore`: Fuga de Secretos y `.git` a la Imagen Docker (CRÍTICO)
- **Archivos Afectados:**
  - [Dockerfile](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/Dockerfile#L40)
- **Evidencia Técnica:**
  El archivo `.dockerignore` **NO EXISTE** en la raíz del proyecto. En la línea 40 de `Dockerfile` se ejecuta:
  ```dockerfile
  COPY . .
  ```
- **Impacto:** Al construir la imagen (`docker build`), se copian al interior del contenedor `/app`:
  - Los archivos `.env` y `.env.prod` con contraseñas de base de datos, credenciales SMTP de Gmail y API Keys de Gemini.
  - La carpeta `.git/` completa con todo el historial.
  - Los backups `.sql` y `.json`.
  Cualquiera que descargue la imagen o ejecute un `docker export` / `docker exec` tiene acceso irrestricto a los secretos más sensibles de la infraestructura.

#### 1.3. Secretos Vivos en Texto Plano en el Espacio de Trabajo (CRÍTICO)
- **Archivos Afectados:**
  - [.env](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/.env#L19-L22)
  - [.env.prod](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/.env.prod#L14-L32)
- **Evidencia Técnica:**
  - `EMAIL_HOST_PASSWORD="fokn czeh uury uezx"` (Contraseña de aplicación real de Gmail).
  - `GEMINI_API_KEY="AIzaSyA4lWvIztuPFKRWZKQ3a9PMLal4mPG57-A"` (Clave API activa de Google Gemini).
  - `DB_PASSWORD=4MbXoPloqA-FyIJdCMK1RwpF-XiWiDxdHx8GcpJTEQc` (Password de base de datos).
  - En [.env.prod](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/.env.prod#L4), `SECRET_KEY` utiliza un valor predeterminado inseguro.

#### 1.4. Inyección de Código HTML/JavaScript (Stored XSS) vía Filtro `|safe` (ALTO)
- **Archivos Afectados:**
  - [profile.html](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/profiles/templates/profiles/profile.html#L135): `{{ user_profile.bio|safe }}`
  - [event_detail.html](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/posts/event_detail.html#L188): `{{ event.description|safe }}`
  - [article_detail.html](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/library/templates/library/article_detail.html#L45): `{{ article.content|safe }}`
- **Evidencia Técnica:**
  Ninguno de estos campos cuenta con saneamiento en backend mediante librerías como `nh3` o `bleach` en sus respectivos métodos `clean()` de formularios o modelos. 
- **Impacto:** Un usuario malintencionado edita su biografía o crea una quedada con `<script>fetch('/api/chat/conversations/').then(...)</script>` y toma el control de las sesiones de cualquier usuario (incluidos administradores) que visite su perfil o el evento.

#### 1.5. Cross-Site WebSocket Hijacking (CSWSH) en Daphne/Channels (ALTO)
- **Archivos Afectados:**
  - [asgi.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/asgi.py#L22-L29)
- **Evidencia Técnica:**
  ```python
  application = ProtocolTypeRouter({
      "http": django_asgi_app,
      "websocket": AuthMiddlewareStack(
          URLRouter(
              chat.routing.websocket_urlpatterns
          )
      ),
  })
  ```
  No se utiliza `AllowedHostsOriginValidator`. La especificación WebSocket no aplica la política de mismo origen (Same-Origin Policy).
- **Impacto:** Cualquier sitio web malicioso abierto en el navegador de un usuario autenticado puede abrir un WebSocket hacia `ws://141.148.227.48/ws/chat/<id>/`, el navegador adjuntará las cookies de sesión automáticamente y el atacante podrá espiar y transmitir mensajes en nombre de la víctima.

#### 1.6. Subida Arbitraria de Archivos y Exposición en `/media/` (ALTO)
- **Archivos Afectados:**
  - [api_views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/chat/api_views.py#L288-L310)
  - [default.conf](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/nginx/default.conf#L18-L21)
- **Evidencia Técnica:**
  En `MessageUploadView`, si el archivo no coincide con prefijos `image/`, `video/` o `audio/`, se le asigna `attachment_type = 'document'` sin validar extensiones permitidas (`.html`, `.svg`, `.exe`, `.js`, etc.).
  Luego, Nginx sirve la ruta `/media/` de forma plana:
  ```nginx
  location /media/ {
      alias /app/media/;
  }
  ```
  Sin cabeceras `Content-Disposition: attachment`, sin `X-Content-Type-Options: nosniff` y sin restringir tipos ejecutables.
- **Impacto:** Subida de archivos SVG o HTML maliciosos que, al ser visualizados en el mismo dominio, ejecutan JavaScript en el contexto de la aplicación.

#### 1.7. Abuso de Servidor de Correo como Relay de Spam en ContactFormView (ALTO)
- **Archivos Afectados:**
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/views.py#L319-L345)
- **Evidencia Técnica:**
  ```python
  email = EmailMultiAlternatives(
      subject,
      text_content,
      settings.DEFAULT_FROM_EMAIL,
      [recipient_email],
      cc=[contact_message.email], # <--- PELIGRO EXTREMO
  )
  ```
  Cualquier visitante anónimo puede enviar el formulario de contacto con un `contact_message.email` arbitrario. El servidor envía una copia (CC) automática con el texto del atacante.
- **Impacto:** No hay CAPTCHA, no hay rate-limiting. La aplicación puede ser utilizada como botnet de correo masivo para campañas de phishing, provocando el baneo inmediato de la cuenta de Gmail y de la IP pública del servidor.

#### 1.8. Modificaciones Destructivas de Estado mediante Métodos HTTP `GET` (CSRF) (MEDIO)
- **Archivos Afectados:**
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/posts/views.py#L803-L825) (`duplicate_event`)
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/posts/views.py#L401-L435) (`toggle_attendance`)
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/profiles/views.py#L243-L253) (`delete_hobby`)
- **Evidencia Técnica:**
  Estas funciones no cuentan con el decorador `@require_POST` ni `@login_required` (en el caso de `duplicate_event` y `toggle_attendance`).
- **Impacto:** Una simple etiqueta `<img src="http://dominio/events/event/1/duplicate/">` o `<img src="http://dominio/profile/delete_hobby/5/">` en un foro o web externa fuerza al usuario autenticado a mutar datos sin su consentimiento.

#### 1.9. Redirección Abierta (Open Redirect) en Marketplace (MEDIO)
- **Archivos Afectados:**
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/marketplace/views.py#L133-L135)
- **Evidencia Técnica:**
  ```python
  next_url = request.POST.get('next', reverse('marketplace:listing_list'))
  return redirect(next_url)
  ```
  No se valida que `next_url` pertenezca al dominio seguro mediante `django.utils.http.url_has_allowed_host_and_scheme`.
- **Impacto:** Un atacante puede crear un enlace que, tras calificar un producto, redirija al usuario a una página de login falsa (phishing).

#### 1.10. Ausencia Total de HTTPS, HSTS y Cabeceras de Seguridad (ALTO)
- **Archivos Afectados:**
  - [default.conf](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/nginx/default.conf#L5-L16)
  - [settings.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/settings.py#L270-L277)
  - [.env.prod](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/.env.prod#L28)
- **Evidencia Técnica:**
  - `listen 80;` en Nginx sin configuración SSL/TLS.
  - `SECURE_SSL_REDIRECT=False`, `SESSION_COOKIE_SECURE=False`, `CSRF_COOKIE_SECURE=False`.
  - Ausencia de cabeceras en Nginx: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`.
  - Ausencia de configuración de Rate Limiting en Nginx (`limit_req_zone`).

---

### EJE 2: Principios SOLID & Filosofía Gentleman (Alan Buscaglia)

#### 2.1. Total Ausencia de TypeScript: Ilusión de Seguridad de Tipos
- **Archivos Afectados:**
  - [package.json](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/package.json#L12-L29)
  - Directorio [frontend/src/](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src)
- **Diagnóstico:**
  En `package.json` aparecen dependencias dev de `@types/react` y `@types/react-dom`, pero **`typescript` no está instalado**, no existe `tsconfig.json` y el 100% de los archivos son `.jsx` o `.js`.
- **Crítica Arquitectónica:** En la metodología de Alan Buscaglia, la **Domain-Driven Design (DDD)** y el **TypeScript Estricto** son innegociables para evitar la degradación del modelo. Acá se consume la API cruda (`res.data`) y se asumen propiedades mágicas que se propagan sin contratos formales (`interface User`, `interface MessageDto`). Un cambio en el backend rompe silenciosamente la UI en producción en tiempo de ejecución.

#### 2.2. Violación del Principio de Responsabilidad Única (SRP) - "God Components" y "God Views"
- **Archivos Afectados:**
  - [MessageArea.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/components/MessageArea.jsx#L24-L752) (752 líneas)
  - [ChatApp.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/ChatApp.jsx#L12-L351) (351 líneas)
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/posts/views.py#L1-L940) (940 líneas)
- **Diagnóstico:**
  - `MessageArea.jsx` acumula más de 8 responsabilidades distintas:
    1. Lógica de WebSocket y recepción de payloads en tiempo real.
    2. Peticiones HTTP manuales con Axios (mensajes, miembros, historial, read receipts).
    3. Manejo de hardware y grabación de notas de voz vía `MediaRecorder` API.
    4. Carga y previsualización de archivos en base64/objectURL.
    5. Renderizado de buscador y modal de participantes.
    6. Renderizado y gestión de solicitudes de acceso (Join Requests).
    7. Integración de panel de emojis con detección de clics fuera del contenedor.
    8. Renderizado del timeline de chat y parseo de hipervínculos por Regex.
  - En el backend, `posts/views.py` gestiona posts, comentarios, likes, eventos, asistencias, duplicaciones, tags y filtros en un solo archivo monolítico de casi 1.000 líneas.

#### 2.3. Inexistencia del Patrón Container - Presentational (Smart vs. Dumb Components)
- **Archivos Afectados:**
  - [GroupCreator.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/components/GroupCreator.jsx#L5-L170)
  - [MessageArea.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/components/MessageArea.jsx#L24-L752)
- **Diagnóstico:**
  No existe separación entre lógica y presentación. Ningún componente es puramente presentacional (Dumb). Todo componente hace su propio `axios.get`, maneja estado mutable complejo, extrae tokens del DOM y renderiza marcado HTML directamente. Es imposible testear la UI sin simular llamadas de red, estado global y eventos de ventana.

#### 2.4. Violación del Principio de Inversión de Dependencias (DIP) y Falta de Capa Anti-Corrupción (ACL)
- **Archivos Afectados:**
  - [ChatApp.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/ChatApp.jsx#L142-L146)
  - [GroupCreator.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/components/GroupCreator.jsx#L54-L63)
  - [MessageArea.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/components/MessageArea.jsx#L148-L154)
- **Diagnóstico:**
  Los componentes de alto nivel dependen de detalles de bajísimo nivel:
  ```javascript
  const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
  axios.post('/api/chat/groups/create/', ...
  ```
  Esta línea exacta se repite de manera artesanal y copiada en 5 archivos distintos.
  - No existe un cliente HTTP centralizado ni interceptores de Axios.
  - No existen Servicios/Repositorios (`ChatRepository`, `UserRepository`).
  - No existen Mappers/Adapters que transformen las respuestas del backend (`api_serializers.py`) a modelos de dominio limpios para el frontend. Los componentes están atados íntimamente a cómo Django nombra los campos en su base de datos.

#### 2.5. Violación del Principio Open/Closed (OCP)
- **Archivos Afectados:**
  - [MessageArea.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/components/MessageArea.jsx#L598-L620)
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/notifications/views.py#L22-L48)
  - [services.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/gamification/services.py#L8-L47)
- **Diagnóstico:**
  Para soportar un nuevo tipo de adjunto o un nuevo tipo de notificación, hay que entrar a meter más cláusulas `else if` en el renderizado o en las vistas de redirección. No se implementa un patrón Strategy ni polimorfismo.

#### 2.6. Gestión de Estado Fragmentada e Inconsistente (Polling vs. WebSockets)
- **Archivos Afectados:**
  - [ChatApp.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/ChatApp.jsx#L95-L135)
- **Diagnóstico:**
  A pesar de tener implementado Django Channels y WebSockets en `MessageArea`:
  - `ChatApp.jsx` ejecuta un polling ciego por HTTP mediante `setInterval` cada 15 segundos para `fetchUnreadCount` y `fetchConversations`.
  - No hay sincronización ni estado compartido unificado (como Redux, Zustand o Signals). El estado de no leídos por polling compite y se desincroniza con los eventos del WebSocket.

---

### EJE 3: Arquitectura de Software General & Production Readiness

#### 3.1. Explosión de Consultas N+1 y Operaciones Síncronas en Señales (Grave Bloqueo de Rendimiento)
- **Archivos Afectados:**
  - [signals.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/gamification/signals.py#L6-L12)
  - [services.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/gamification/services.py#L8-L27)
- **Evidencia Técnica:**
  Ante CADA "like" (`m2m_changed` en `Posts.likes`), la señal ejecuta:
  ```python
  posts = Posts.objects.filter(user=user)
  total_likes = sum(post.likes.count() for post in posts) # <--- N+1 QUERIES
  
  events = Event.objects.filter(organizer=user)
  for event in events: # <--- N+1 QUERIES
      physical = event.attendances.filter(attendance_type='physical').count()
      online = event.attendances.filter(attendance_type='online').count()
  ```
  Si el usuario tiene 50 publicaciones y 20 eventos, un solo click en el botón de "like" dispara más de 90 consultas SQL inmediatas y bloqueantes a MariaDB. A esto se le suma el envío síncrono de emails (`send_mail`).
- **Impacto:** Bajo concurrencia real, el servidor agota el pool de conexiones de base de datos (`CONN_MAX_AGE=600`) y se produce una denegación de servicio (DoS) autoinfligida.

#### 3.2. Envíos de Correo Síncronos Bloqueando el Hilo de Trabajo (Falta de Cola de Mensajería)
- **Archivos Afectados:**
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/posts/views.py#L264-L269)
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/views.py#L272-L278)
  - [views.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/views.py#L344)
- **Diagnóstico:**
  Las vistas ejecutan `email.send()` directamente en el proceso HTTP de Django/Daphne. Si el servidor SMTP de Gmail tarda 3 segundos en responder o sufre un timeout, la petición del usuario se congela durante ese tiempo.
- **Solución Requerida:** Celery, RQ o Dramatiq respaldado por el Redis que ya está corriendo en la infraestructura.

#### 3.3. Manejo de Errores Descentralizado y Falta de Error Boundaries
- **Archivos Afectados:**
  - Backend: [settings.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/settings.py#L209-L216) (Falta `EXCEPTION_HANDLER` en `REST_FRAMEWORK`).
  - Frontend: [ChatApp.jsx](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/ChatApp.jsx)
- **Diagnóstico:**
  - En backend, excepciones no controladas devuelven páginas HTML de error de Django 500 en lugar de JSON estructurado normalizado.
  - En frontend, no existe un `<ErrorBoundary>`. Si se produce un error al renderizar un mensaje o un participante con datos inesperados, la aplicación de chat se desmonta por completo dejando un panel blanco sin mensaje de recuperación.

#### 3.4. Estrategia de Testing Absolutamente Deficiente
- **Evidencia Técnica:**
  - [chat/tests.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/chat/tests.py#L1-L3): Archivo vacío (3 líneas, solo el template por defecto).
  - [gamification/tests.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/gamification/tests.py#L1-L3): Archivo vacío.
  - [marketplace/tests.py](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/marketplace/tests.py#L1-L3): Archivo vacío.
  - **Frontend:** Cero archivos de test. Ni Vitest, ni Jest, ni React Testing Library configurados en `package.json`.
- **Impacto:** Cualquier cambio de código para solucionar un bug de seguridad tiene una probabilidad altísima de provocar regresiones no detectadas.

---

## 4. Risks (Matriz de Riesgos para Producción)

| Riesgo | Severidad | Probabilidad | Impacto |
| :--- | :---: | :---: | :--- |
| **Exposición y Filtración de Base de Datos y Secretos** (Git & Docker) | **CRÍTICA** | Inmediata | Exfiltración de hashes de usuarios, toma de control del servidor y de cuentas de correo vinculadas. |
| **Compromiso de Cuentas vía Stored XSS** (`bio|safe`, `description|safe`) | **ALTA** | Alta | Secuestro de sesiones de administradores y usuarios normales mediante ejecución de scripts en perfiles y eventos. |
| **Secuestro de WebSocket (CSWSH)** (`asgi.py`) | **ALTA** | Alta | Espionaje y envío de mensajes en chats privados desde sitios externos sin autorización del usuario. |
| **Relay Masivo de Spam por Correo** (`ContactFormView`) | **ALTA** | Muy Alta | Bloqueo y suspensión de la cuenta de Google/Gmail y de la reputación del servidor. |
| **Colapso de Base de Datos por N+1 en Gamificación** | **ALTA** | Alta | Bloqueo de peticiones y DoS cuando se acumulen likes y eventos en el sistema. |
| **Modificación de Estado por Peticiones GET / CSRF** | **MEDIA** | Alta | Duplicación masiva involuntaria de eventos y eliminación de datos por navegación externa. |
| **Pérdida de Sesiones y Datos por HTTP plano (Sin TLS)** | **ALTA** | Inmediata | Interceptación Man-in-the-Middle de contraseñas y cookies de sesión en redes públicas. |

---

## 5. Next Recommended (Plan de Acción Priorizado)

```
FASE 0: CONTENCIÓN Y PURGA INMEDIATA (Día 1)
 ├── 1. Purga de Git: BFG Repo-Cleaner / git-filter-repo para eliminar volcados .sql, .json y cookies.
 ├── 2. Rotación obligatoria de todos los secretos: Contraseñas de BD, SECRET_KEY, App Passwords de Gmail y Gemini API Keys.
 ├── 3. Creación inmediata de .dockerignore excluyendo .env*, .git, *.sql, *.json, logs y node_modules.
 └── 4. Inclusión de .env*, cookies.txt, backups y logs en .gitignore.

FASE 1: PARCHADO CRÍTICO DE SEGURIDAD (Días 2 - 3)
 ├── 1. Sanitización de HTML: Eliminar |safe o instalar nh3/bleach en backend antes de persistir bio, eventos y artículos.
 ├── 2. Proteger ASGI: Incorporar AllowedHostsOriginValidator en aficionados_network/asgi.py.
 ├── 3. Restringir subidas de archivos: Validar extensiones estrictas en chat y configurar Nginx con cabeceras nosniff y Content-Disposition.
 ├── 4. Blindar el formulario de contacto: Eliminar el CC automático al correo ingresado y añadir rate limiting/reCAPTCHA.
 ├── 5. Forzar métodos POST: Decorar con @require_POST y @login_required las vistas destructivas (duplicate, toggle_attendance, delete_hobby).
 ├── 6. Corregir Open Redirect en Marketplace validando next con url_has_allowed_host_and_scheme.
 └── 7. Habilitar HTTPS/SSL en Nginx mediante Certbot y activar cabeceras de seguridad estrictas en settings.py.

FASE 2: ARQUITECTURA BACKEND & RENDIMIENTO (Semana 2)
 ├── 1. Eliminar bucle N+1 en gamification/services.py: Reemplazar bucles con agregaciones SQL (annotate, Count, Subquery).
 ├── 2. Desacoplar envíos de correo mediante Celery o Dramatiq con Redis para no bloquear workers HTTP.
 └── 3. Completar suites de tests unitarios e integrales en chat, gamification y marketplace.

FASE 3: REFACTORIZACIÓN FRONTEND - GENTLEMAN & SOLID (Semanas 3 - 4)
 ├── 1. Migrar Frontend a TypeScript estricto (tsconfig.json, interfaces de dominio, eliminación total de tipos implícitos).
 ├── 2. Implementar Capa Anti-Corrupción y Cliente HTTP centralizado (Axios con interceptor automático para CSRF, servicios api/chat.service.ts).
 ├── 3. Dividir MessageArea.jsx (752 líneas) aplicando Container-Presentational:
 │     ├── hooks/useChatRecorder.ts (Manejo de audio)
 │     ├── hooks/useMessageHistory.ts (Gestión de estado y paginación)
 │     ├── components/MessageTimeline.tsx (Dumb component)
 │     ├── components/MessageInput.tsx (Dumb component)
 │     └── components/AttachmentPreview.tsx (Dumb component)
 └── 4. Unificar la gestión de estado (Zustand o React Context) eliminando el polling redundante de 15 segundos en favor de eventos WebSocket bidireccionales.
```

---
*Reporte generado por Antigravity Senior Architect. Criterio de producción: Cero tolerancia a la mediocridad técnica.*
