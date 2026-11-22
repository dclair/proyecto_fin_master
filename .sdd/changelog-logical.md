# Logical Changelog

**Last reviewed:** 2026-11-22  
**Purpose:** semantic change history of the system, independent from Git commits.

This log records meaningful product/architecture/testing changes. Use it to understand how the system evolved and what behavior changed.

## 2026-11-22: Fix CSS Cascade Order and Specificity for TomSelect and Form Controls in Dark Mode

**Type:** bug fix / UI / architecture  
**Status:** done

What changed:
- **Inversión de Precedencia en `<head>` (`layout.html`)**:
  - Reubicado el bloque `{% block extra_css %}` para que se inserte antes de `style.css`.
  - Con esto, cualquier CDN de terceros (como TomSelect o TinyMCE) se carga primero, permitiendo que las reglas de `style.css` de Hubs&Clicks sobreescriban estilos sin colisión de cascada.
- **Blindaje Semántico Dark Mode en `style.css`**:
  - Implementados selectores calificados `[data-bs-theme="dark"]` con `!important` para `.ts-wrapper`, `.ts-control`, `.ts-dropdown`, `.ts-dropdown .option`, headers y campos de texto (`.ts-control input`), erradicando fondos blancos `#fff` y textos oscuros `#343a40` del CDN de TomSelect.
  - Anulado `background-image` en `.ts-wrapper.form-select` para evitar duplicidad de caret indicator de Bootstrap y TomSelect.
  - Blindaje con `!important` para elementos nativos `<select>`, `.form-select` y sus `<option>` en modo oscuro.
- **Sincronización de Caché Estática en Producción Docker**:
  - Ejecutado `collectstatic` en contenedor `web` y local (generando `style.f57013f5c2b3.css` con cache buster `?v=3.2`).
  - Reiniciado el contenedor `web` para invalidar el manifest de `ManifestStaticFilesStorage` en la memoria del proceso Daphne.

Why:
- Resolver el defecto visual donde en `/biblioteca/crear/` el desplegable de "Terapia (existente)" aparecía con fondo blanco y texto en negro en Tema Oscuro tras reiniciar Hubs&Clicks.

Impact:
- Contraste semántico perfecto (WCAG AA) en todos los desplegables de la biblioteca y plataforma en tema oscuro, garantizando consistencia visual y robustez en la precedencia de estilos.

## 2026-11-19: Chat Document Presentation, Clean Filenames, Custom PDF Badges & Sanitizer Link Fix

**Type:** feature / UI / bugfix / security
**Status:** done

What changed:
- **Visualización Enriquecida de Adjuntos en el Chat**:
  - Propiedad `@property attachment_name` en `Message` (`chat/models.py`) que extrae el nombre base y limpia sufijos aleatorios internos de colisión de Django manteniendo palabras y nombres legítimos.
  - Exposición de `attachment_name` en `MessageSerializer` (`chat/api_serializers.py`) y en el payload del broadcast de Channels (`chat/api_views.py` y `chat/consumers.py`).
  - Sincronización en frontend (`useWebSocket.js`, `chat.types.ts`) para retener `attachment_name` en tiempo real.
  - Rediseño de adjuntos en `MessageTimeline.jsx`:
    - Tarjetas diferenciadas con componentes SVG de `lucide-react`.
    - PDFs destacados con badge rojo "PDF", icono `FileText`, nombre original en negrita y botón de descarga directa de 1 solo clic (`?download=1`).
    - Detección e iconografía diferenciada para hojas de cálculo (`FileSpreadsheet`), documentos de texto (`FileText`), archivos comprimidos (`FileArchive`) y código/texto plano (`FileCode`).
    - Previsualización en el compositor (`AttachmentPreview.jsx`) con badges e iconos temáticos.
- **Descarga Operativa con 1 Clic**:
  - Soporte de parámetro `?download=1` en `ProtectedAttachmentDownloadView` (`chat/api_views.py`), fijando `Content-Disposition: attachment; filename="{filename}"` y manteniendo `inline` para visualización directa en visor de navegador.
- **Corrección de Sanitizador HTML (`nh3`)**:
  - Resuelto conflicto en `aficionados_network/utils/sanitizer.py` donde `link_rel` colisionaba con atributos manuales en enlaces permitidos, previniendo errores 500 al guardar publicaciones y artículos.
- **Infraestructura y Red**:
  - Exposición de puerto 8000 en Nginx (`nginx/default.conf`) y configuración de orígenes confiables CSRF dinámicos por puerto.

Why:
- Mejorar la experiencia de usuario en el chat, permitiendo identificar instantáneamente el tipo y nombre real de los documentos compartidos (especialmente PDFs clínicos y terapéuticos) y descargarlos de manera inmediata.

Impact:
- Interfaz de chat profesional y accesible en modo claro y oscuro, con nombres de archivo legibles, previsualización exacta y descargas operativas seguras.

## 2026-11-18: Production Hardening, Protected Media, WebSockets Security, Celery + Redis & Gmail SMTP Verification

**Type:** security / architecture / infrastructure / performance
**Status:** done

What changed:
- **Blindaje de Archivos Privados & Mitigación IDOR en /media/**:
  - Nginx bloquea el acceso público directo a `/media/chat_attachments/` con `deny all; return 404;`.
  - Configurado bloque interno Nginx `location /protected_media/` con cabeceras `X-Content-Type-Options: nosniff` y CSP estricto `default-src 'none'; sandbox`.
  - Implementada vista segura `ProtectedAttachmentDownloadView` en `chat/api_views.py` que despacha adjuntos vía cabecera `X-Accel-Redirect` (producción) o `FileResponse` (desarrollo), verificando pertenencia a la conversación.
- **Validación Binaria de Archivos (Magic Bytes) y Sanitización EXIF**:
  - En `MessageUploadView` (`chat/api_views.py`), se inspeccionan firmas reales de bytes para JPG, PNG, GIF, WEBP y PDF.
  - Las imágenes se re-procesan con Pillow eliminando metadatos EXIF de geolocalización y dispositivo antes del guardado.
- **Autorización Estricta en Reseñas de Eventos**:
  - En `profiles/views.py` (`add_review`), se prohíbe que el organizador se auto-califique, se exige que `request.user` haya participado en el evento y que la fecha del evento ya haya transcurrido.
- **Robustez y Seguridad en WebSockets (Channels)**:
  - En `chat/consumers.py`, se capturan excepciones de decodificación JSON, se limitan los mensajes a 4000 caracteres y se valida continuamente que el usuario sea participante activo antes de despachar al canal.
- **Cola de Tareas Asíncrona Resiliente con Celery + Redis**:
  - Añadido `celery[redis]` a `requirements.txt`.
  - Creados `aficionados_network/celery.py` y `aficionados_network/tasks.py` (`send_email_task`) con reintentos exponenciales automáticos y jitter.
  - `mailer.py` adaptado para despachar mediante Celery con contingencia in-process (`ThreadPoolExecutor`).
  - Añadido servicio `celery_worker` a `docker-compose.yml`.
- **Hardening de Nginx y Optimización de Tests**:
  - Zonas de limitación de tasa de peticiones (`limit_req_zone`) en Nginx para `/login/` y `/register/`, cabecera `Strict-Transport-Security` (HSTS) y `X-Forwarded-Proto`.
  - Configuración desacoplada en `settings.py` para testing (`InMemoryChannelLayer`, `CompressedStaticFilesStorage`, `MD5PasswordHasher`, `CELERY_TASK_ALWAYS_EAGER`).
- **Verificación SMTP Real de Gmail**:
  - Validado el envío en vivo contra servidores de Google (`smtp.gmail.com:587`) mediante Contraseña de Aplicación de Google (`EMAIL_HOST_PASSWORD`), confirmando entrega efectiva de correo de activación de cuenta con plantilla corporativa y logo CID a `jmdclair@gmail.com`.
- **Suite de Pruebas**:
  - 80/80 tests pasando en 100% verde en ~6.9s.

Why:
- Blindar la plataforma ante vulnerabilidades de acceso indebido, fugas de privacidad y denegación de servicio antes del paso a producción.
- Desacoplar el envío de correos del ciclo de petición-respuesta HTTP para garantizar resiliencia.

Impact:
- Sistema totalmente auditado, protegido y con cobertura de pruebas completa.

## 2026-09-03: Ágora Channel, Multimedia Posts, Text Sanitization, Post Explorer & Dark Mode Harmonization

**Type:** feature / architecture / UI / security
**Status:** done

What changed:
- **Canal Oficial Ágora**:
  - Auto-asignación automática en registro (`profiles/signals.py`) y migración histórica universal (`0010_assign_agora_to_all_profiles`).
  - Restricción estricta de selección y publicación para usuarios `is_staff=True` en `PostCreateForm` y `EventForm`.
  - Badges destacados `.badge-agora` y `.badge-agora-solid` en naranja fuerte (`#ea580c`) con icono de escudo oficial (`bi-shield-fill-check`).
  - Priorización fija al inicio (índice 0) en Home feeds y explorador mediante anotación `Case/When` (`is_agora`) en el ORM de Django.
- **Publicaciones Multimedia No Excluyentes y PDF**:
  - Habilitada la combinación simultánea de imagen, video corto, enlace genérico y documento PDF adjunto con descarga directa y badge representativo.
- **Exploración de Publicaciones (`/events/posts/`)**:
  - Creada CBV `PostListView` con búsqueda multi-campo, filtro por terapia y paginación en bloques de 12 elementos.
  - Añadido botón píldora simétrico *"Ver todas las publicaciones"* en la Home.
- **Selectores de Terapias con TomSelect**:
  - Orden alfabético forzado (`Hobby.Meta.ordering = ["name"]`) con buscador predictivo y carga asíncrona resiliente a la hidratación de Vite.
- **Motor de Sanitización de Texto Plano**:
  - Propiedades `@property plain_text_summary` (`Article`), `@property plain_text_caption` (`Posts`) y `@property plain_text_description` (`Event`) que decodifican entidades HTML (`&eacute;`, `&nbsp;`), evitan palabras aglutinadas y limpian el texto para tarjetas resumen.
- **Armonización de Modo Oscuro (Dark Theme)**:
  - Eliminado `bg-light` en `.recommended-events-box` y `.nav-pills-hubs`.
  - Aplicados fondos nativos oscuros (`var(--bs-body-bg)`), bordes verde turquesa corporativo (`1.5px solid var(--hubs-primary)`, `#2ba1ab`), textos inactivos en blanco puro (`#ffffff`) y badges con contadores numéricos en color.
  - Versión de assets CSS incrementada a `?v=2.0`.

Why:
- Dotar a la asociación de un canal institucional indiscutible con visibilidad 100% garantizada.
- Evitar fallos de renderizado y entidades HTML crudas generadas por TinyMCE.
- Ofrecer máxima simetría y coherencia estética en modo oscuro.

Impact:
- Experiencia de usuario y rendimiento óptimos con suite de tests ampliada (32 tests unitarios pasando en verde).


**Type:** feature / bug fix / security
**Status:** done

What changed:
- Removed `.env.prod` from Git tracking and added to `.gitignore` to prevent secret leakage.
- Added a `try/except` block in `ContactView` to handle `SMTPException` (e.g. 500 error from Gmail auth failures) gracefully.
- Fixed a bug where the login success message showed the email instead of the username.
- Fixed layout issues in `my_events.html` (mobile horizontal scroll and table headers).
- Increased the `UserProfile.bio` character limit from 500 to 1500.
- Implemented local image upload functionality for TinyMCE in the profile edit view, saving images to `media/tinymce/`.

Why:
- To secure production credentials and prevent them from being exposed in public repositories.
- To prevent the application from crashing on the contact page if SMTP credentials fail.
- To provide a more personalized login experience.
- To allow therapists more space to explain their services and integrate local images natively without relying on external URLs.

Impact:
- Enhanced security, stability, and a significantly improved user experience for profile editing.

## 2026-06-11: UI Refinements, "Quedada" to "Evento" Migration & Select2 Integration

**Type:** feature / UI
**Status:** done

What changed:
- Migrated the "Quedada" terminology to "Evento" across the codebase and user interface for better clarity.
- Implemented smooth hover effects for navbar elements.
- Integrated a searchable dropdown menu for categories in the event discovery view to improve navigation efficiency.

Why:
- Standardize terminology to something more universally understood and professional.
- Enhance the overall look and feel of the platform with subtle animations and better form controls.

Impact:
- Improved user experience and interface consistency.

## 2026-06-10: Notification HTMX Deletion, Like Bug Fix & Modal Contrast

**Type:** feature / bug fix
**Status:** done

What changed:
- Finalized the notification system by implementing individual and bulk deletion capabilities using HTMX (`hx-delete`, `hx-target`).
- Resolved a JavaScript bug preventing "Like" functionality in the event detail view by fixing the toggle logic.
- Fixed text contrast issues inside modal dialogs to ensure readability across different themes.

Why:
- Provide users with full control over their notification history without page reloads.
- Ensure core interaction features (Likes) function flawlessly.
- Maintain high accessibility standards in all UI components, including modals.

Impact:
- Users can seamlessly manage notifications.
- The event interaction loop is fully restored.

## 2026-06-09: Dark Mode UI/UX Accessibility & Chat Isolation

**Type:** feature / UI / accessibility
**Status:** done

What changed:
- Audited and refined dark mode across the platform to fix low-contrast text on light backgrounds (especially in Event Cards, User Profiles, and "Últimos Clicks" badges).
- Implemented adaptive utility classes in CSS (`.text-dark-mode-hubs`, `.dark-mode-text-dark`, etc.) scoped under `[data-bs-theme="dark"]`.
- Added sticky-sidebar scrolling fixes for the Event Creation layout.
- Added real-time user search functionality to the `GroupCreator.jsx` React component.
- Isolated the React Chat panel from the global dark mode by wrapping it with `data-bs-theme="light"`, preventing unreadable text interactions with its hardcoded background colors.

Why:
- To ensure professional accessibility standards and visual consistency regardless of the user's theme preference.
- To prevent UI conflicts in the complex chat DOM without requiring a complete CSS rewrite of the React components.

Impact:
- Users now have a pristine dark mode experience on all standard Django views.
- The Chat application functions flawlessly in permanent light mode, avoiding text invisibility issues.

## 2026-06-07: Search Enhancements, Reviews, and Therapy Filters

**Type:** feature / UI
**Status:** done

What changed:
- Upgraded the global directory search (`ProfilesListView`) and Chat user search to filter simultaneously by `username`, `first_name`, `last_name`, and `email` using Django `Q` objects.
- Added email display to user cards across the application (Directory, Chat, Group Creator) to help distinguish between users with identical names.
- Validated and finalized the Event Reviews (Star Rating) system, ensuring users can rate event organizers from the "Mis Citas" view.
- Implemented the "Mis Terapias" fast filter on the events list (`EventListView`), allowing logged-in users to instantly filter events that match their registered hobbies/therapies.
- Updated `README.md` to reflect 100% completion of the project roadmap.

Why:
- To drastically improve the UX of finding specific users or therapists in a growing platform.
- To provide quick access to relevant events, boosting user engagement.
- To mark the technical completion of the core MVP features.

Impact:
- The UI is more informative and filters are highly responsive.
- The project is officially feature-complete according to the initial roadmap.

## 2026-06-07: Hybrid Event Attendance & Infinite Scroll UI Optimization

**Type:** feature / UI
**Status:** done

What changed:
- Implemented `EventAttendance` through-model for `Event.participants` to support hybrid event types (Physical vs Online).
- Updated max_participants validation to only restrict physical attendees, allowing unlimited online participants.
- Reduced the size of user profile cards in the `Comunidad de Terapeutas` directory (`col-lg-3`, smaller images).
- Implemented dynamic infinite scrolling for the user directory using HTMX, replacing traditional pagination.
- Renamed general navigation labels to "Comunidad de Terapeutas" / "Terapia" across the platform.

Why:
- To allow real-world capacity control for physical events while enabling broader online participation.
- To improve frontend performance and user experience when browsing a large directory of therapists.
- To use more accurate and professional terminology aligning with the project's focus on natural therapies.

Impact:
- Database schema changed (`EventAttendance` through-model introduced and migrated).
- Backend pagination logic bypassed for HTMX requests to serve partial HTML fragments seamlessly.

## 2026-06-05: Real-Time Chat with Multimedia and Advanced Deletion

**Type:** feature / architecture
**Status:** done

What changed:
- Integrated Django Channels (WebSockets) for real-time messaging.
- Built a React-based frontend (`ChatApp.jsx`, `MessageArea.jsx`) embedded in the Django template.
- Implemented 1-on-1 and Group Chat capabilities with admin roles and join requests.
- Added multimedia support (images, videos, documents) via a hybrid API upload strategy + WebSocket broadcast.
- Implemented "Delete for everyone" (physical DB/file deletion).
- Implemented "Delete for me" (logical deletion via `hidden_by` ManyToMany relation).

Why:
- To provide a modern, WhatsApp-like real-time messaging experience for users.
- To handle heavy file uploads securely via standard HTTP while maintaining real-time UX via WebSockets.
- To provide users with control over their data (deleting mistakes) and safety (hiding inappropriate received content).

Impact:
- The platform now has a fully functional, real-time communication layer.
- New database tables: `Conversation`, `ConversationParticipant`, `Message`, `GroupJoinRequest`.
- Redis is now required for Channels layer in production.

## 2026-06-01: Project Knowledge Base Established

**Type:** documentation / operational knowledge  
**Status:** done

Added structured project knowledge under `.sdd/knowledge/`:

- `project-architecture-hubs-clicks.md`
- `testing-strategy-hubs-clicks.md`

Captured:

- Product purpose.
- Stack.
- Directory structure.
- Apps and model map.
- URL map.
- View flows.
- Templates and assets.
- Signals.
- Admin surface.
- Testing strategy.
- Caveats and operational notes.

Impact:

- Future developers and AI agents can understand the project without re-discovering everything from source.
- `.sdd/README.md` points to the main knowledge documents.

## 2026-06-01: Test Baseline Added

**Type:** testing / quality  
**Status:** done

Added/reworked tests in:

- `aficionados_network/test.py`
- `profiles/tests/tests_models.py`
- `profiles/tests/tests_views.py`
- `posts/tests.py`
- `notifications/tests.py`

Current result:

```text
35 tests passing with SQLite
```

Default command:

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py test --verbosity 1
```

Behavior now covered:

- Auth, registration activation, contact form and emails.
- Profile models, follows, hobbies, reviews.
- Profile routes.
- Post likes/comments and emails.
- Event lifecycle.
- Hobby hub and clicks gallery.
- Notification signals, unread count, list, redirects.

Impact:

- Manual repeated testing burden is much lower.
- Future changes should update or extend tests before being considered complete.

## 2026-06-01: Contact Email Template Path Fixed

**Type:** bug fix  
**Status:** done

Changed `ContactFormView` template path from:

```text
emails/notification_email.html
```

to:

```text
general/emails/notification_email.html
```

Why:

- The old path did not match the existing template tree.
- The new test suite exposed the mismatch.

Impact:

- Contact form can render and send the branded HTML email using the existing template.
- The behavior is covered by `aficionados_network/test.py`.

## 2026-05-25: SQLite To MySQL/MariaDB Migration Implemented

**Type:** database / deployment readiness  
**Status:** done

Implemented environment-selected database backend:

- SQLite fallback.
- MySQL/MariaDB with `utf8mb4`.
- PyMySQL fallback when `mysqlclient` is unavailable.
- Shell env vars can override `.env`.

Artifacts:

- `.sdd/changes/sqlite-to-mysql-migration/`
- `.sdd/knowledge/django-sqlite-to-mysql-mariadb.md`

Operational lessons:

- Signals must guard `raw=True` during fixture loads.
- Flatpages and sites need careful fixture handling.
- Media files are not migrated by DB dump/load.
- App DB permissions should be scoped.

Impact:

- Project can run against SQLite or MySQL/MariaDB depending on `DB_ENGINE`.
- Test command should explicitly select SQLite unless DB-specific behavior is being validated.

## Earlier: Core Hubs&Clicks Features Built

**Type:** product baseline  
**Status:** existing before current `.sdd` work

Feature areas already present:

- Social profiles.
- Hobbies and user hobby levels.
- Follows.
- Clicks/posts with images.
- Likes and comments.
- Events.
- Event participation.
- Event cancellation/reactivation/duplication.
- Event comments.
- Organizer reviews.
- In-app notifications.
- Branded HTML emails.
- Contact form.
- Legal/static pages.
- Cookie banner assets.

Impact:

- The system is a functional Django social/event platform.
- New work should treat these as existing product contracts unless explicitly changing them.

## How To Add Future Entries

Use this shape:

```text
## YYYY-MM-DD: Short Semantic Title

**Type:** feature | bug fix | testing | docs | architecture | database | deployment
**Status:** proposed | in progress | done | reverted

What changed:
- ...

Why:
- ...

Impact:
- ...

Verification:
- ...
```

Record product behavior changes, architectural decisions, testing baselines, migrations, and bug fixes. Do not record trivial formatting-only edits unless they affect operating knowledge.
