# Decision Log

**Last reviewed:** 2026-11-25  
**Purpose:** record important technical/product decisions and why they were made.

This is not a commit log. It captures decisions that future developers and AI agents should understand before changing direction.

## D-001: Keep Django Server-Rendered Architecture

**Date:** before 2026-06-01  
**Decision:** Hubs&Clicks remains a server-rendered Django application with templates, Bootstrap, vanilla JS, AJAX, and selective HTMX-style partial responses.

**Why:**

- The current codebase is organized around Django views, forms, templates, messages, and context processors.
- User workflows are conventional CRUD/social flows that do not require SPA complexity.
- Server rendering keeps auth, forms, redirects, messages, and email-triggering interactions straightforward.

**Implications:**

- New features should prefer Django views/forms/templates unless there is a strong reason otherwise.
- JS should enhance interactions, not replace core server behavior.
- Tests should verify redirects, templates, context, DB rows, emails, and notifications.

## D-002: Use Environment-Selected Database Backend

**Date:** 2026-05-25 migration work  
**Decision:** `DB_ENGINE` selects SQLite or MySQL/MariaDB in `settings.py`.

**Why:**

- SQLite is convenient for local fallback and fast tests.
- MySQL/MariaDB is better for production-like concurrency and deployment.
- Shell environment override allows recovery and test commands without editing `.env`.

**Implications:**

- Use `env DB_ENGINE=sqlite ...` for local tests by default.
- Use MySQL/MariaDB runs only when validating database-specific behavior.
- Do not change `load_dotenv()` to override shell environment variables.

## D-003: Prefer PyMySQL Fallback For MySQL Compatibility

**Date:** 2026-05-25 migration work  
**Decision:** If `mysqlclient`/`MySQLdb` is unavailable and `pymysql` exists, install PyMySQL as MySQLdb before Django loads the backend.

**Why:**

- Avoids requiring native MySQL development headers in local environments.
- Keeps Django's MySQL backend usable with a pure-Python driver.
- A Django 6 compatibility version patch is present in settings.

**Implications:**

- Keep the fallback near the top of `settings.py`.
- Re-test MySQL behavior after driver/version changes.

## D-004: Keep Hobbies As Shared Domain Taxonomy

**Date:** before 2026-06-01  
**Decision:** `profiles.Hobby` is the shared category/interest model across profiles, posts, and events.

**Why:**

- Users express interests through hobbies.
- Posts are categorized by hobby.
- Events belong to hobbies.
- Event matching and hub pages depend on a common taxonomy.

**Implications:**

- Do not create a separate post category or event category model unless there is a strong product reason.
- Changes to `Hobby` can affect profile editing, post creation, event creation, hubs, filters, and tests.

## D-005: Store User Hobby Level In Through Model

**Date:** before 2026-06-01  
**Decision:** User hobby experience is stored in `profiles.UserHobby`, not directly on `UserProfile` or `Hobby`.

**Why:**

- A user can have different levels for different hobbies.
- Event matching needs per-hobby user level.
- The unique `(profile, hobby)` constraint prevents duplicated interests.

**Implications:**

- Match/mentor logic should query `UserHobby`.
- Adding fields to hobby membership means changing the through model and tests.

## D-006: Preserve Dual Notification Surfaces

**Date:** before 2026-06-01  
**Decision:** Important interactions often create both an in-app notification and a branded HTML email.

**Why:**

- In-app notifications support return visits and activity history.
- Emails notify users who are away from the app.
- The product README describes this as a core communication/branding feature.

**Implications:**

- When modifying likes, comments, event attendance, cancellation, reactivation, follows, or reviews, check both notification and email behavior.
- Tests should assert both DB notifications and `mail.outbox` where applicable.

## D-007: Make Signals Fixture-Safe

**Date:** 2026-05-25 migration work  
**Decision:** Signals that create related rows must return early when `kwargs.get("raw")` is true.

**Why:**

- `loaddata` saves objects with `raw=True`.
- During fixture loading, related objects may not exist yet.
- Signal side effects can corrupt imports or fail migrations.

**Implications:**

- Any future signal must include a raw-load guard if it touches related data.
- Test fixture loading if adding non-trivial signals.

## D-008: Establish SQLite Test Baseline

**Date:** 2026-06-01  
**Decision:** The default development test command uses SQLite and explicit `DEBUG=True`.

**Why:**

- The local `.env` may select MySQL.
- Sandbox/local permission restrictions can block MySQL sockets.
- Tests should be fast and deterministic for day-to-day development.

**Command:**

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py test --verbosity 1
```

**Implications:**

- Use `override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)` in route tests.
- Use locmem email backend in email tests.
- Add MySQL-specific runs only when validating database behavior.

## D-009: Use Temporary Media Roots In Upload Tests

**Date:** 2026-06-01  
**Decision:** Tests that upload images should use a temporary `MEDIA_ROOT`.

**Why:**

- Upload tests should not pollute project `media/`.
- Failed tests should not leave persistent files.

**Implications:**

- Future upload tests should follow the `posts/tests.py` pattern.
- File deletion behavior should assert against temp paths.

## D-010: Fix Contact Email Template Path

**Date:** 2026-06-01  
**Decision:** `ContactFormView` renders `general/emails/notification_email.html`.

**Why:**

- The previous path `emails/notification_email.html` did not match the template tree.
- The contact form test exposed the mismatch.

**Implications:**

- Contact emails now use the same existing branded notification template path as the rest of the app.
- If email templates are reorganized, update tests and this decision.

## D-011: Canal Oficial Institucional Ágora y Asignación Forzada en Registro

**Date:** 2026-09-03  
**Decision:** `Ágora` (`slug="agora"`) se define como el canal institucional exclusivo de la dirección/junta. Se asigna automáticamente a todo nuevo usuario en `profiles/signals.py` como su primera terapia y se aplicó una migración de datos histórica (`0010_assign_agora_to_all_profiles`) a todas las cuentas preexistentes.

**Why:**
- Evita que los comunicados oficiales queden invisibles si un usuario olvida o no sabe que debe suscribirse manualmente a Ágora.
- Garantiza difusión 100% universal para convocatorias, normativas y avisos institucionales.

**Implications:**
- Todo nuevo usuario registrado tendrá garantizado el canal en `user.profile.hobbies`.
- Los tests de usuario deben contemplar que `profile.hobbies.filter(slug='agora').exists()` es `True` por defecto.

## D-012: Restricción de Publicación en Ágora a Usuarios Staff (`is_staff`)

**Date:** 2026-09-03  
**Decision:** La selección de `Ágora` en formularios de publicación (`PostCreateForm`, `EventForm`, etc.) está filtrada en backend. Si el usuario autenticado no tiene `is_staff=True`, la categoría Ágora es excluida de los querysets del campo del formulario y rechazada en validación.

**Why:**
- Solo administradores y miembros de la junta directiva deben tener autoridad para emitir mensajes oficiales con la identidad institucional.

**Implications:**
- Los usuarios regulares nunca verán Ágora como opción seleccionable para sus publicaciones individuales.
- El backend rechaza cualquier manipulación maliciosa de `category_id`.

## D-013: Priorización de Contenidos Institucionales mediante `Case/When` en el ORM

**Date:** 2026-09-03  
**Decision:** En lugar de realizar consultas separadas y concatenar listas en Python (lo que destruiría la paginación del ORM y la eficiencia de memoria), las publicaciones, eventos y artículos se ordenan anotando condicionalmente `is_agora = Case(When(category__slug="agora", then=Value(1)), default=Value(0), output_field=IntegerField())` y ordenando por `("-is_agora", "-created_at")`.

**Why:**
- Permite que los comunicados oficiales aparezcan **fijados al inicio (índice 0)** de las secciones de la Home y Exploración de Publicaciones, sin perder la evaluación perezosa (*lazy evaluation*), `select_related`, `prefetch_related` ni `LIMIT/OFFSET`.

**Implications:**
- Las consultas permanecen en una sola instrucción SQL optimizada.
- Los tests verifican que objetos con `slug="agora"` preceden a objetos más recientes de otras categorías.

## D-014: Propiedades de Extracción y Sanitización de Texto Plano en Modelos

**Date:** 2026-09-03  
**Decision:** Implementar `@property plain_text_summary` (`Article`), `@property plain_text_caption` (`Posts`) y `@property plain_text_description` (`Event`) a nivel de modelo para el renderizado en tarjetas resumen, en lugar de confiar en el filtro de plantilla `striptags`.

**Why:**
- Los editores enriquecidos (TinyMCE) producen entidades HTML (`&eacute;`, `&nbsp;`, `&oacute;`). El filtro `striptags` no decodifica entidades y elimina `<br>` sin agregar espacios, pegando palabras adyacentes (`primaveralLa`).
- Las propiedades en el modelo centralizan la sustitución de bloques con espacios, eliminación de HTML, decodificación vía `html.unescape()` y normalización de espacios, asegurando texto 100% natural.

**Implications:**
- Las tarjetas resumen de toda la plataforma usan estas propiedades antes del filtro `truncatewords`/`truncatechars`.

## D-015: Arquitectura de Alto Contraste en Modo Oscuro para Bloques y Navegación

**Date:** 2026-09-03  
**Decision:** Eliminar la clase utilitaria `bg-light` de contenedores de nivel superior (`.recommended-events-box` y `.nav-pills-hubs`). En modo oscuro, estos contenedores adoptan `var(--bs-body-bg)`, borde `1.5px solid var(--hubs-primary)` (`#2ba1ab`), textos en `#ffffff` y contadores de insignias con fondo blanco y tipografía en color corporativo.

**Why:**
- Bootstrap 5 asigna a `.bg-light` un valor con `!important` que genera recuadros descoloridos en modo oscuro, rompiendo la inmersión visual.

**Implications:**
- Se mantiene perfecta armonía visual entre bloques contiguos en la Home.
- Las insignias y textos inactivos conservan máxima legibilidad (accesibilidad WCAG AA).

## D-016: Blindaje de Archivos Privados en Media con Nginx Internal y X-Accel-Redirect

**Date:** 2026-11-18  
**Decision:** Bloquear en Nginx el acceso directo a `/media/chat_attachments/` (`deny all; return 404;`) y servir los adjuntos privados exclusivamente a través de una vista Django autenticada (`ProtectedAttachmentDownloadView`) que emite la cabecera `X-Accel-Redirect: /protected_media/...` apuntando a un bloque Nginx con directiva `internal;`.

**Why:**
- Evita el IDOR (Insecure Direct Object Reference) y la fuga de privacidad donde cualquier usuario no autenticado con la URL directa podía descargar adjuntos confidenciales de conversaciones ajenas.
- Descarga el peso del streaming de bytes de Python/Django a Nginx una vez superado el control de permisos de la conversación en Django.

**Implications:**
- Los adjuntos de chat se descargan vía `/api/chat/attachments/<uuid:message_id>/download/`.
- Django valida que `request.user` pertenezca a `conversation.participants`.
- En modo `DEBUG`, se recurre a `FileResponse` transparente para desarrollo local sin Nginx.

## D-017: Validación de Archivos por Magic Bytes y Sanitización EXIF con Pillow

**Date:** 2026-11-18  
**Decision:** En `MessageUploadView` (`chat/api_views.py`), los adjuntos no se validan únicamente por la extensión del archivo (`.jpg`, `.png`, etc.), sino leyendo las firmas binarias reales (*magic bytes* para JPG, PNG, GIF, WEBP y PDF) y re-encodeando las imágenes con Pillow para eliminar metadatos EXIF sensibles (geolocalización, cámara) antes de guardarlas en disco.

**Why:**
- Evita la subida de ejecutables o scripts maliciosos camuflados con doble extensión (ej. `payload.php.jpg`).
- Protege la privacidad de los usuarios eliminando coordenadas GPS incrustadas en fotos tomadas con dispositivos móviles.

**Implications:**
- Cualquier archivo cuya firma real no coincida con el MIME permitido es rechazado con error 400.
- Todas las imágenes subidas al chat quedan estandarizadas y limpias de metadatos.

## D-018: Autorización Estricta en Reseñas de Eventos (Anti-Auto-Reseña y Verificación de Asistencia)

**Date:** 2026-11-18  
**Decision:** En `profiles/views.py` (`add_review`), se impuso una validación triple para poder calificar al organizador de un evento: (1) `request.user != event.organizer` (prohibido autocalificarse), (2) `event.participants.filter(id=request.user.id).exists()` (asistencia obligatoria comprobada), y (3) `event.event_date <= timezone.now()` (el evento debe haber finalizado).

**Why:**
- Elimina la manipulación de reputación y las reseñas fraudulentas de usuarios que no participaron o sobre eventos futuros.

**Implications:**
- Las valoraciones reflejan con exactitud la experiencia real de asistentes verificados.

## D-019: Robustez y Blindaje en WebSockets con Django Channels

**Date:** 2026-11-18  
**Decision:** En `chat/consumers.py`, se capturan excepciones de decodificación JSON en `receive()`, se impone un límite estricto de longitud de mensaje (`<= 4000` caracteres), y se re-verifica `is_participant` en cada mensaje enviado al canal en tiempo real.

**Why:**
- Protege los workers Daphne de caídas por payloads JSON corruptos o ataques de denegación de servicio por flooding de strings gigantes.
- Asegura que si un usuario es expulsado del grupo mientras mantiene el WebSocket abierto, no pueda seguir inyectando mensajes.

**Implications:**
- Conexiones en tiempo real tolerantes a fallos y protegidas contra abusos.

## D-020: Configuración de Entorno de Tests Optimizado en Memoria

**Date:** 2026-11-18  
**Decision:** Cuando `TESTING = 'test' in sys.argv` en `aficionados_network/settings.py`:
- `CHANNEL_LAYERS` utiliza `InMemoryChannelLayer` en lugar de Redis.
- `STORAGES["staticfiles"]` utiliza `CompressedStaticFilesStorage` en lugar de `ManifestStaticFilesStorage` estricto.
- `PASSWORD_HASHERS` prioriza `MD5PasswordHasher` para acelerar la creación de usuarios en fixtures.
- `CELERY_TASK_ALWAYS_EAGER = True` y `CELERY_TASK_EAGER_PROPAGATES = True`.

**Why:**
- Desacopla la suite de pruebas automatizadas de dependencias de servicios externos (Redis vivo, compilación de manifest de estáticos).
- Reduce drásticamente el tiempo de ejecución de la suite (de ~45s con PBKDF2 a ~6.9s para 80 tests).

**Implications:**
- Los tests corren en cualquier entorno o CI sin servicios satélites y con velocidad extrema.

## D-021: Despacho Asíncrono Resiliente de Correo con Celery, Redis y Backoff Exponencial

**Date:** 2026-11-18  
**Decision:** Sustituir el despacho de correos atado al hilo HTTP por una tarea encolada en Celery (`send_email_task`) con backend/broker Redis, política de reintentos exponenciales con jitter (`autoretry_for=(Exception,)`, `max_retries=5`), y un fallback defensivo en `mailer.py` mediante `ThreadPoolExecutor` si Celery o Redis no están disponibles.

**Why:**
- Las conexiones SMTP externas (como Gmail) introducen latencias variables y posibles reintentos que bloquean peticiones HTTP del usuario o se pierden si hay un microcorte.
- El fallback en `mailer.py` asegura que, incluso si Redis cayera, el usuario no experimente caídas 500 y el correo intente enviarse en background.

**Implications:**
- Cero latencia en respuestas HTTP de formularios de contacto y eventos.
- Máxima resiliencia y tolerancia a fallos transitorios de red.

## D-022: Programación Periódica con Celery Beat e Idempotencia Multinivel para Recordatorios de Eventos

**Date:** 2026-11-22  
**Decision:** Implementar el envío automatizado de recordatorios para quedadas que inician en las siguientes 24 horas mediante Celery Beat programado a las 08:00 AM (`crontab(hour=8, minute=0)`), ejecutando la tarea `posts.tasks.send_event_reminders_task`.

**Why:**

- Los usuarios necesitan recordar con 24 horas de antelación sus quedadas programadas para planificar su asistencia presencial u online.
- Se debe impedir categóricamente el envío repetido de correos ante caídas del worker, reintentos de red o reinicios de Celery Beat.
- El despachador debe integrarse de forma desacoplada con el `NotificationDispatcher` y el modelo `Notification`.

**Architecture & Implementation Details:**

1. **Idempotencia Multinivel:**
   - **Nivel Persistencia:** Se agregaron `reminder_sent` (booleano) y `reminder_sent_at` (timestamp) al modelo `EventAttendance`, con índice `(event, reminder_sent)` para consultas optimizadas.
   - **Nivel Dominio / Defensivo:** Antes de despachar, se verifica si ya existe un registro `Notification.objects.filter(recipient=user, event=event, notification_type='event_reminder')`. Si existe, se sincroniza el flag en la asistencia sin reenviar el correo.
   - **Transaccionalidad Atómica:** Cada asistente se procesa bajo `transaction.atomic()` asegurando aislamiento individual frente a caídas imprevistas.
2. **Desacoplamiento Celery Beat en Docker Compose:**
   - Servicio independiente `celery_beat` en `docker-compose.yml` ejecutando `celery -A aficionados_network beat -l info`. Evita la duplicación de eventos de cron que ocurriría si beat estuviese acoplado a los workers al escalar réplicas horizontales en producción.
3. **Plantillas Dedicadas y NotificationDispatcher:**
   - Se añadió el tipo `event_reminder` a las opciones de `Notification`.
   - Se crearon plantillas personalizadas `aficionados_network/templates/emails/event_reminder.html` y `event_reminder.txt` con la identidad visual de Hubs & Clicks y soporte para sesiones presenciales y online.
   - Propagación de `template_name` y `extra_context` serializable por Celery a través de `NotificationDispatcher` y `mailer.py`.

**Implications:**

- Zero duplicate emails garantizado por diseño en cualquier escenario de fallo.
- Asistentes desapuntados, usuarios inactivos o eventos cancelados/eliminados quedan automáticamente excluidos del envío.

## D-023: Arquitectura Zero-Downtime SSL/TLS Readiness con Certbot Webroot y Nginx

**Date:** 2026-11-22  
**Decision:** Implementar la infraestructura perimetral de "Zero-Downtime SSL Readiness" mediante el enfoque ACME Webroot compartido entre Nginx y Certbot en Docker Compose, plantilla declarativa de producción (`nginx/production-ssl.conf.template`) y runbook operativo exhaustivo (`docs/runbook-ssl.md` y `.sdd/runbook-ssl.md`).

**Why:**

- El entorno de producción corre actualmente sobre HTTP (`http://141.148.227.48`) a la espera de la asignación y compra del dominio oficial.
- El enfoque ingenuo de Certbot en modo "Standalone" requiere apagar Nginx para escuchar en el puerto 80, provocando caída de servicio total e interrupción de conexiones WebSocket durante la expedición inicial y renovaciones.
- Se debe garantizar que el paso a HTTPS en el momento en que se apunte el dominio sea instantáneo, seguro y 100% libre de downtime, sin romper la operación actual en HTTP.

**Architecture & Implementation Details:**

1. **Enrutamiento ACME Webroot en Nginx (`nginx/default.conf`):**
   - Se añadió `location /.well-known/acme-challenge/ { root /var/www/certbot; }` al servidor actual en puertos 80/8000.
   - Permite que Let's Encrypt verifique el dominio directamente a través del Nginx en ejecución, sin apagar ningún servicio ni modificar las reglas de proxy reverso a Daphne/Django ni la protección de adjuntos (`X-Accel-Redirect`).
2. **Volúmenes Compartidos y Servicio Certbot (`docker-compose.yml`):**
   - Volúmenes dedicados `certbot_www` (para los tokens de desafío ACME) y `certbot_conf` (para las claves privadas y certificados en `/etc/letsencrypt`).
   - Servicio `certbot` basado en `certbot/certbot:latest` preparado tanto para ejecución bajo demanda (`docker compose run --rm certbot ...`) como para ejecución continua como daemon (`while :; do certbot renew; sleep 12h ...`).
   - Mapeo preventivo del puerto `443:443` en Nginx.
3. **Plantilla de Producción SSL Declarativa (`nginx/production-ssl.conf.template`):**
   - Servidor HTTP (80) exclusivo para resolución de desafíos ACME y redirección permanente `301 https://$host$request_uri`.
   - Servidor HTTPS (443) con TLS 1.2/1.3, ciphers modernos (ECDHE-ECDSA/RSA-AES-GCM), session cache de 10m y tickets deshabilitados, HSTS estricto (`max-age=31536000`), cabeceras anti-sniff y clickjacking, y soporte completo para WebSockets Daphne (`/ws/`) y media protegida.
   - Diseñado para inyección parametrizada segura vía `envsubst '${DOMAIN}'`.
4. **Runbook y Gestión de Cookies Seguras:**
   - Procedimiento de 5 pasos documentado y reproducible con validación previa de DNS y simulación de contingencia/rollback.
   - Parametrización en `.env.prod` lista para activar `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True` y `SECURE_HSTS_SECONDS=31536000`.

**Implications:**

- Cero riesgo de interrupción operativa en el entorno HTTP actual.
- Transición a HTTPS en menos de 2 minutos una vez delegado el DNS.
- Renovaciones automáticas transparentes sin caída de servicio.

## D-024: Re-arquitectura Semántica del Tema Oscuro con Bootstrap 5.3 y React Microfrontend

**Date:** 2026-11-22  
**Decision:** Adoptar el Camino A (Saneamiento Quirúrgico y Migración Semántica a Bootstrap 5.3) en lugar de una re-arquitectura con design tokens propietarios, normalizando la jerarquía de elevación tonal en CSS, purgando clases anti-patrón de 35 templates Django y sincronizando de forma reactiva el microfrontend de React y editores WYSIWYG.

**Why:**

- La auditoría técnica identificó 87 ocurrencias de `text-dark` que causaban contraste ciego (1.15:1) en modo oscuro y 113 contenedores con `bg-white` o `bg-light` fijos que generaban parches blancos cegadores.
- Existían parches destructivos como `.dark-mode-text-dark` en `style.css` que forzaban texto oscuro dentro de modo oscuro para compensar clases rígidas.
- El microfrontend de React (`ChatApp.tsx`) tenía forzado `data-bs-theme="light"` en el portal, permaneciendo completamente desacoplado del selector de tema del host Django.
- Crear un sistema de tokens propietario (Camino B) hubiera roto `crispy-forms` y modales nativos de Bootstrap, introduciendo sobreingeniería innecesaria.

**Architecture & Implementation Details:**

1. **Tokens Semánticos y Eliminación de Parches (`static/css/style.css`):**
   - Configurada la jerarquía de elevación tonal para `[data-bs-theme="dark"]` (`--bs-body-bg: #121614`, `--bs-card-bg: #1b231e`, `--bs-tertiary-bg: #2a362f`, `--bs-body-color: #e4ebe6`, `--bs-border-color: #354239`) con contraste verificado WCAG AAA/AA.
   - Purgada la clase `.dark-mode-text-dark` y corregida la inversión de `--hubs-dark`.
   - Soporte semántico unificado para Crispy Forms y TomSelect (`.ts-control`, `.ts-dropdown`) sin requerir estilos locales.
2. **Barrido Semántico en 35 Templates Django:**
   - Erradicadas todas las clases de parche y bloques `<style>` locales con `#fff !important`.
   - Migración de `bg-white` a `bg-transparent` en cabeceras de cards y a `bg-body` / `bg-body-secondary` en contenedores.
   - Reemplazo de `bg-light` por `bg-body-tertiary` y `text-dark` por `text-body` / `text-body-emphasis`.
3. **Sincronización React Microfrontend (`frontend/src/`):**
   - Implementado el hook `useHostTheme` con triple canal reactivo: lectura DOM/localStorage, escucha del CustomEvent `themeChanged` emitido por `theme-toggle.js` y `MutationObserver` defensivo sobre `document.documentElement[data-bs-theme]`.
   - `ChatApp.css` y subcomponentes adaptados a variables nativas de Bootstrap 5.3 y soporte dinámico en `EmojiPicker`.
4. **Editores TinyMCE Dinámicos:**
   - Inyección reactiva de `skin: oxide-dark` y `content_css: dark` ante conmutación de tema en vivo.

**Implications:**

- 100% de cumplimiento con WCAG AA (> 4.5:1) en modo oscuro y claro.
- Código limpio sin duplicación de CSS ni especificidades forzadas.
- Sincronización instantánea en tiempo real entre Django y el microfrontend de React sin recargar la página.

## D-025: Inversión del Orden de Cascada CSS y Blindaje de Especificidad para Componentes de Terceros (TomSelect)

**Date:** 2026-11-22  
**Decision:** Reubicar el bloque `{% block extra_css %}` en `layout.html` ANTES de la hoja de estilos principal `style.css` y blindar los estilos de TomSelect y controles de formulario con `[data-bs-theme="dark"]` y `!important` para evitar que estilos CDN aplasten la tematización semántica.

**Why:**

- En `/biblioteca/crear/`, el desplegable de "Terapia (existente)" renderizado con TomSelect continuaba apareciendo con fondo blanco y texto en negro en Tema Oscuro.
- La causa raíz fue doble:
  1. `tom-select.bootstrap5.min.css` se cargaba en `{% block extra_css %}`, ubicado después de `style.css` en `layout.html`, ganando la precedencia de la cascada ante igual especificidad.
  2. El CDN de TomSelect contiene estilos rígidos (`color: #343a40; background: #fff`) para `.ts-dropdown` y `.ts-control` que no estaban cualificados con el selector de tema de Bootstrap 5.3.
  3. En producción, Daphne mantiene en memoria el manifest de `ManifestStaticFilesStorage`, requiriendo reinicio del contenedor `web` tras `collectstatic` para emitir las URLs con el hash actualizado.

**Architecture & Implementation Details:**

1. **Orden de Cascada en `layout.html`:**
   - CDN y librerías externas en `{% block extra_css %}` se evalúan primero.
   - `style.css` se evalúa después, garantizando la última palabra para estilos de marca y tema.
2. **Blindaje de Selectores en `style.css`:**
   - Se añadieron selectores calificados `[data-bs-theme="dark"] .ts-wrapper`, `[data-bs-theme="dark"] .ts-dropdown`, `[data-bs-theme="dark"] .ts-control input`, etc., asignando variables semánticas (`--bs-body-bg`, `--bs-card-bg`, `--bs-body-color`).
   - Se anuló el `background-image` en `.ts-wrapper.form-select` para prevenir flechas duplicadas con TomSelect.
3. **Ciclo de Vida de Estáticos en Docker:**
   - Sincronización vía `collectstatic` dentro del contenedor web y en local.
   - Incremento del cache buster a `?v=3.2`.
   - Reinicio del contenedor `web` (`docker restart proyecto_fin_master_v2-web-1`).

**Implications:**

- Cualquier componente de terceros inyectado en plantillas hijas respetará obligatoriamente la jerarquía visual de Hubs&Clicks.
- 100% de consistencia de Tema Oscuro en todos los desplegables TomSelect y nativos de la plataforma.

## D-026: Hardening Institucional del Canal Ágora en Marketplace y Restricción de Publicación a Staff

**Date:** 2026-11-24  
**Decision:** Excluir la categoría institucional "Ágora" (`slug="agora"`) de los selectores de categoría en creación y edición de anuncios del Mercadillo (`marketplace/forms.py`) para usuarios no administradores (`not request.user.is_staff`), y reforzar la validación limpia a nivel servidor en `clean_hobby` para prevenir manipulaciones de payloads POST.

**Why:**
- El canal "Ágora" es una categoría de uso estrictamente institucional (reservada a anuncios oficiales de la directiva y comunicados colegiales).
- Aunque ya estaba blindada en Posts y Biblioteca Clínica, un terapeuta estándar podía publicar anuncios en el Mercadillo bajo la categoría Ágora si conocía su ID.

**Architecture & Implementation Details:**
1. En `ListingCreateView` y `ListingUpdateView`, se inyecta `request.user` en los `get_form_kwargs()`.
2. En `ListingForm.__init__`, si el usuario no es staff, se filtra el queryset del campo `hobby` con `.exclude(slug="agora")`.
3. En `ListingForm.clean_hobby`, se valida que un usuario regular no pueda asignar `slug="agora"`, levantando un `ValidationError` descriptivo.
4. Cobertura completa de pruebas agregada a `marketplace/tests.py`.

**Implications:**
- Blindaje homogéneo del canal institucional en todos los módulos de contenido del sistema.
- Cero anuncios no oficiales en los feeds prioritarios de Ágora.

## D-027: Arquitectura Bimodal del Home (Hero de Captación para Visitantes vs. Cockpit de Bienvenida para Miembros)

**Date:** 2026-11-24  
**Decision:** Implementar una experiencia bimodal en la portada (`home.html`): Hero de captación institucional y propuesta de valor con doble Call To Action para usuarios anónimos, y Cockpit de bienvenida personalizado con pulso de actividad y accesos directos para usuarios autenticados.

**Why:**
- La portada carecía de elementos de motivación y propuesta de valor para terapeutas que llegaban por primera vez sin cuenta activa, reduciendo la conversión de registro.
- Para terapeutas ya autenticados, se generaba redundancia visual con mensajes flash duplicados de login y bloques repetitivos de eventos ya presentes en las pestañas inferiores.

**Architecture & Implementation Details:**
1. **Visitantes Anónimos:** Hero con titular motivacional (*"El punto de encuentro para terapeutas y apasionados de las terapias naturales"*), resumen de valor, doble CTA (*"Unirme a la Comunidad"* -> `/register/`, *"Explorar Terapias"* -> scroll a `#homeTabs`), 3 píldoras de social proof (Comunidad Verificada, Biblioteca de Casos, Quedadas) e ilustración del ecosistema.
2. **Miembros Autenticados:** Cockpit con avatar del usuario, saludo personalizado (*"¡Hola de nuevo, [Nombre]! 👋"*), subtítulo contextual y botones de acción rápida (*"Crear Publicación"*, *"Proponer Plan"*).
3. **Eliminación de Redundancias:** Se suprimió el mensaje flash duplicado `messages.success(..., f"¡Bienvenido/a {user.username}!")` de `LoginView.form_valid`, el carrusel horizontal duplicado de eventos recomendados, y se ajustó el copy de pestaña a *"Últimos Eventos"* para reflejar la realidad cronológica de eventos concluidos.

**Implications:**
- Clara separación de objetivos de UX entre conversión (anónimos) y productividad comunitaria (logueados).

## D-028: Rediseño Semántico y Verificación Institucional en el Registro de Terapeutas

**Date:** 2026-11-24  
**Decision:** Rediseñar visual y funcionalmente el formulario de registro (`register.html` y `RegisterForm`) organizándolo en dos bloques semánticos con iconografía integrada, alternador de visualización de contraseña y aviso previo de verificación institucional.

**Why:**
- El formulario de registro previo presentaba una estética tosca que desentonaba con la identidad cuidada de la plataforma y no explicaba el proceso de validación del número de colegiado/socio.

**Architecture & Implementation Details:**
1. Estructura en tarjeta con fondo adaptativo (`bg-body`), bordes redondeados (`rounded-4`) y sombra sutil.
2. Bloque 1: *Datos de Membresía y Profesión* (`first_name`, `razon_social`, `numero_socio`).
3. Bloque 2: *Credenciales y Acceso* (`username`, `email`, `password1`, `password2`).
4. Iconos descriptivos en `input-group-text` y botones de alternar visibilidad de clave (`bi-eye` / `bi-eye-slash`) con script en vainilla JS accesible.
5. Banner institucional informativo: *"Verificación institucional: Para garantizar un entorno seguro y riguroso, comprobaremos tus datos de socio antes de activar el acceso completo a la comunidad. Mantente atento a tu email."*.

**Implications:**
- Alta tasa de confianza inicial en el proceso de onboarding y estética unificada con el resto de formularios del sistema.

## D-029: Soporte Dinámico para Acceso Multi-Dispositivo Móvil en Red Local (LAN)

**Date:** 2026-11-24  
**Decision:** Configurar detección automática y no intrusiva de la dirección IP local de la interfaz LAN en `settings.py` cuando `DEBUG=True`, incorporándola a `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` y comunicándola a `DJANGO_VITE` y Vite Dev Server (`0.0.0.0:5173`).

**Why:**
- Permitir al desarrollador probar y auditar la experiencia de usuario real en smartphones conectados a la misma red WiFi local sin modificar manualmente archivos de configuración ni romper URLs de producción o desarrollo habitual en `localhost`.

**Architecture & Implementation Details:**
1. `settings.py` resuelve mediante socket UDP dummy (`8.8.8.8:80`) la IP LAN activa del host (ej. `192.168.1.134`) y la añade dinámicamente a `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.
2. `DJANGO_VITE` utiliza `VITE_DEV_SERVER_HOST = LOCAL_LAN_IP` permitiendo al navegador del smartphone solicitar los bundles React a la IP de la máquina host en lugar de a `localhost`.
3. `frontend/vite.config.ts` configurado con `server: { host: '0.0.0.0', port: 5173, cors: true }`.
4. `start_dev.sh` arranca Django en `0.0.0.0:8000`, Vite en `0.0.0.0:5173` y presenta en terminal la URL directa para móviles.

**Implications:**
- Pruebas en dispositivos móviles sin fricción ni riesgos de commits con IPs estáticas cableadas.

## D-030: Filtrado de Eventos Pasados y Empty State Explicativo en Exploración de Eventos

**Date:** 2026-11-24  
**Decision:** Incorporar soporte para el parámetro `show_past=true` en `EventListView`, sustituir el mensaje vacío ambiguo por un Empty State descriptivo con opciones de acción rápida y marcar visualmente los eventos concluidos con badge "Finalizado".

**Why:**
- Cuando no había eventos futuros programados, la vista mostraba un texto confuso (*"No hemos encontrado quedadas con estos filtros."*) incluso sin filtros aplicados, impidiendo al terapeuta consultar eventos o talleres que ya habían tenido lugar.

**Architecture & Implementation Details:**
1. `EventListView.get_queryset` evalúa `show_past`: por defecto solo muestra eventos a futuro (`event_date__gte=now`), pero si `show_past=true`, lista todos los eventos ordenados por `-event_date`.
2. En `event_list.html`, el empty state presenta un diseño cuidado con icono, el texto solicitado: *"NO hemos encontrado eventos futuros aún por realizarse o con los filtros aplicados."*, y un botón directo para consultar todos los eventos preservando los filtros de búsqueda.
3. Se integró un interruptor tipo switch en la barra de filtros para alternar eventos pasados en cualquier momento.
4. Badge contextual `Finalizado` en las tarjetas de eventos pasados mediante la propiedad `@property is_past`.
5. Paginación adaptada para propagar `&show_past=true`.

**Implications:**
- Eliminación de pantallas vacías sin salida y acceso completo a la memoria histórica de eventos de la comunidad.

## D-031: Defensa en Profundidad y Rotación de Secretos (Rate Limiting en Capas, 403 Explícito en Chat API y SECRET_KEY_FALLBACKS)

**Date:** 2026-11-25  
**Decision:** Implementar y verificar cuatro capas críticas de blindaje de seguridad y resiliencia arquitectónica:
1. **Chat API - Rechazo Explícito 403 (Anti-IDOR/BOLA):** En `chat/api_views.py` (`MessageListView`), levantar `PermissionDenied("No eres participante de esta conversación")` en lugar de responder un queryset vacío con 200 OK cuando un usuario no participante intenta consultar los mensajes de una conversación, devolviendo HTTP 403 Forbidden estricto y eliminando ambigüedad o enumeración de identificadores de chat.
2. **Rate Limiting Perimetral en Capas (Nginx & DRF):**
   - En Nginx (`default.conf` y `production-ssl.conf.template`): Protección de fuerza bruta en `/login/`, `/register/`, `/password-reset/` y `/password_reset/` bajo la zona `auth_limit` (`5r/m`, `burst=3-5 nodelay`), y activación de la zona `api_limit:10m` (`rate=60r/m burst=20 nodelay`) para todas las rutas `/api/`.
   - En Django REST Framework (`aficionados_network/settings.py`): Configuración global de limitación de tasa en capas mediante `DEFAULT_THROTTLE_CLASSES` (`AnonRateThrottle`, `UserRateThrottle`) y `DEFAULT_THROTTLE_RATES` (`anon: '60/minute'`, `user: '300/minute'`).
3. **Rotación Zero-Downtime de Secretos:**
   - Soporte nativo para `SECRET_KEY_FALLBACKS = [k.strip() for k in os.getenv("SECRET_KEY_FALLBACKS", "").split(",") if k.strip()]`.
   - Validación defensiva obligatoria en producción (`if not DEBUG:`): Verificación estricta de que ningún fallback sea trivial (`len >= 32`) ni utilice prefijos inseguros (`django-insecure`).
   - Procedimiento de Rotación Cero-Downtime:
     * Paso 1: Generar una nueva clave criptográficamente segura (`python -c "import secrets; print(secrets.token_urlsafe(50))"`).
     * Paso 2: Copiar el valor actual de `SECRET_KEY` en `SECRET_KEY_FALLBACKS` (o añadir a la lista separada por comas) en `.env.prod`.
     * Paso 3: Asignar la nueva clave a `SECRET_KEY` en `.env.prod`.
     * Paso 4: Reiniciar servicios (`docker compose restart web celery_worker celery_beat`). Las sesiones activas de los usuarios y tokens previamente firmados continúan siendo válidos transparentemente vía `SECRET_KEY_FALLBACKS` sin invalidar cookies ni forzar re-autenticación masiva.
     * Paso 5: Cumplido el ciclo de expiración (`SESSION_COOKIE_AGE = 3600`), retirar la clave antigua de los fallbacks.
4. **Verificación Automatizada de Aislamiento:**
   - Cobertura de pruebas con respuesta `403 Forbidden` garantizada para no participantes en API y cierre de conexión para anónimos/no participantes en WebSockets (`ChatConsumer` con `WebsocketCommunicator`).
   - Cobertura de pruebas de aislamiento horizontal en Biblioteca (`ArticleUpdateView` y `ArticleDeleteView` rechazando usuarios ajenos con 403 Forbidden).
   - Cobertura de autorización en borrado de posts (`PostDeleteView`) y eventos (`EventCancelView`, `EventReactivateView`).

**Why:**
- Prevenir ataques de fuerza bruta, credential stuffing y DoS en endpoints sensibles y de API.
- Evitar fugas de información o ambigüedad de estados permitiendo que el cliente detecte claramente la denegación de permisos (403) en lugar de listas vacías indistinguibles de chats sin mensajes.
- Permitir la rotación periódica de credenciales maestras sin degradación del servicio ni disrupción de usuarios logueados.

**Implications:**
- Seguridad perimetral robusta en Nginx combinada con throttling granular en la capa de aplicación.
- Garantía de cero brechas de autorización entre usuarios y 135 tests pasando al 100% en verde.

## D-032: Páginas de Error Corporativas Resilientes (404, 403 y 500 Autocontenida) y Rediseño de Footer Botánico (.footer-hubs)

**Date:** 2026-11-25  
**Decision:**
1. Crear páginas de error corporativas personalizadas: `404.html` (recurso extraviado) y `403.html` (acceso restringido) heredando de `general/layout.html` con estética y navegación congruente.
2. Diseñar la página `500.html` como una plantilla **100% autocontenida y ultra-defensiva**: sin herencia de layout, sin etiquetas `{% static %}` locales de Django y sin interacción con el ORM ni la base de datos MariaDB, utilizando estilos CSS inline y fallback a CDN de Bootstrap.
3. Rediseñar el footer institucional (`.footer-hubs`) en `templates/_includes/_footer.html` y `static/css/style.css` mediante tokens semánticos de anclaje visual verde bosque (`--hubs-footer-bg: #16281e` en claro, `#0c130f` en oscuro) y certificación de contrastes WCAG AAA.

**Why:**
- Ante un error interno del servidor (500) motivado por la caída del motor de base de datos MariaDB o la saturación de conexiones, un template estándar que intente consultar el usuario, perfiles, flatpages o context processors volvería a lanzar una excepción durante el propio renderizado del error, mostrando al usuario la pantalla blanca o el mensaje crudo de error del proxy Nginx.
- Las páginas de error 404 y 403 carecían de branding y guiado de navegación hacia el inicio o soporte.
- El footer presentaba fondo blanco y contraste insuficiente en tema oscuro, rompiendo la inmersión y la jerarquía de lectura del portal.

**Architecture & Implementation Details:**
1. `500.html` incluye inline toda su tipografía, estilos de card (`.error-card`), botones y mensajes de disculpa claros con enlaces directos a `/` y `/contact/`.
2. `404.html` y `403.html` utilizan la tarjeta `bg-body-tertiary rounded-4` con botones píldora corporativos (`btn-hubs`).
3. El footer utiliza variables CSS `:root` y `[data-bs-theme="dark"]` (`--hubs-footer-bg`, `--hubs-footer-border`, `--hubs-footer-text: #c5d3ca`, `--hubs-footer-brand: #8bd3ab`), dotando a la interfaz de anclaje cromático de inspiración botánica y total accesibilidad.

**Implications:**
- Renderizado de errores resiliente a prueba de fallos de infraestructura.
- Identidad visual armónica y accesible en el cierre de todas las vistas.

