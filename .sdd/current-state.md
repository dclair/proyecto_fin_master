# Current State

**Last reviewed:** 2026-11-27  
**Role:** single operational truth for the project today.

This document is the first place to check before modifying Hubs&Clicks. It summarizes what is currently true, what is verified, what is risky, and where deeper details live.

## Product

Hubs&Clicks is a private Django social network for connecting therapists and wellness professionals through hobbies and natural therapies.

Current user-facing capabilities:

- Register with email, activate account, log in, and log out with robust CSRF and session hardening.
- Redesigned Professional Registration: 2-step semantic cards (Membership & Profession / Credentials & Access), password toggles, and institutional verification alert.
- Bimodal Home Architecture:
  - For visitors: Conversion hero with value proposition, double CTA (*"Unirme a la Comunidad"* / *"Explorar Terapias"*), 3 social proof badges (Verified Community, Clinical Library, Meetups/Workshops), and ecosystem illustration.
  - For authenticated members: Welcome Cockpit with personalized avatar greeting (*"¡Hola de nuevo, [Nombre]! 👋"*), activity pulse, and quick content creation shortcuts.
- Edit profile data: avatar, bio (with TinyMCE rich text and local image upload), birth date, location, website, identity fields, and searchable TomSelect hobby/therapy selector with live filtering and alphabetical sorting.
- Add hobbies to profile with experience levels.
- Follow and unfollow other profiles with dynamic follower/following counters.
- Create multi-content posts (Clicks): combines non-exclusive photo, video, generic external link, and attached PDF document (up to 10MB).
- Explore all community posts (`/events/posts/`) with keyword search, therapy filter, clean server-side pagination (12 per page), and symmetric Home button.
- Like and comment on posts.
- Create hobby-based events with TinyMCE rich descriptions and TomSelect searchable category dropdowns sorted alphabetically.
- Join or leave events when allowed, with hybrid support (physical vs. online) and physical capacity limit enforcement.
- Cancel, reactivate, duplicate, edit, and list owned events.
- Explore Events with Past Events Filter & Empty State:
  - Filter toggle switch for *"Ver todos los eventos (incluidos pasados)"* (`show_past=true`).
  - Clear empty state card when no future events match: *"NO hemos encontrado eventos futuros aún por realizarse o con los filtros aplicados."* with quick action button to show past events.
  - Badges contextuales de estado *"Finalizado"* para eventos con fecha cumplida.
- Automatic Chat Synchronization for Online Events: online events generate a private group chat via Django Signals, automatically adding participants upon joining.
- Automated 24h Event Reminders:
  - Scheduled daily at 08:00 AM via Celery Beat (`posts.tasks.send_event_reminders_task`).
  - Sends branded HTML emails with session-specific details (streaming link for online events; physical address for in-person events).
  - Multi-level idempotency guarantee (persisted boolean `reminder_sent`, `reminder_sent_at`, Notification model deduplication, atomic transactions).
- Centralized Notification Dispatcher (`NotificationDispatcher`):
  - In-app notification bell with dynamic badges and HTMX-powered asynchronous clearance (`HX-Trigger`).
  - Branded HTML emails dispatched asynchronously via Celery + Redis with exponential backoff and jitter (5 retries), backed by in-process `ThreadPoolExecutor` contingency.
  - Full business event coverage: likes, comments, follows, event attendance confirmation, 24h reminders, chat group join requests, peer reviews, gamification badges, and clinical library comments/ratings.
- Browse the "Comunidad de Terapeutas" (Therapists Community) with infinite scrolling (HTMX) and multi-field search (username, name, email).
- Review event organizers after participation with a 5-star system (strictly protected: no self-reviews, verified attendance, and only on completed events).
- Send contact messages to the site owner/admin with reply-to headers (safe from email relay abuse).
- Real-Time Messaging & Chat (1-on-1 and Groups):
  - 100% Strict TypeScript React 19 frontend with Vite 8.
  - WebSockets ASGI via Django Channels with `AllowedHostsOriginValidator` (CSWSH mitigated).
  - Protected attachment downloads via Nginx `X-Accel-Redirect` / `ProtectedAttachmentDownloadView` ensuring zero unauthorized access or IDOR.
  - Strict binary upload validation: Magic bytes validation (JPG, PNG, GIF, WEBP, PDF) and Pillow EXIF metadata sanitization.
  - Enriched document presentation: original sanitized filenames (`attachment_name`), custom Lucide icons by file type (red PDF badge, green XLS, blue DOC, amber ZIP, purple code/text), and 1-click direct download (`?download=1`).
  - Full control over messages ("Delete for everyone" with disk destruction, and "Delete for me" local logical deletion).
- Official Institutional Channel "Ágora" (`slug="agora"`):
  - Automatically assigned to all new users upon registration as their default primary therapy.
  - Retroactively assigned to all existing profiles via migration `0010_assign_agora_to_all_profiles`.
  - Publishing strictly restricted to `is_staff` users across Posts, Library, and Marketplace listings.
  - High-visibility orange badge (`.badge-agora` / `.badge-agora-solid`, `#ea580c`) with official shield icon.
  - Pinned to first position (index 0) in Home feeds (Posts, Events, Library) via ORM `Case/When` annotation (`is_agora`).
- Universal Plain-Text Extraction & HTML Entity Sanitization:
  - Properties `Article.plain_text_summary`, `Posts.plain_text_caption`, and `Event.plain_text_description` decode HTML entities (`&eacute;` -> `é`, `&nbsp;` -> ` `) and separate block tags with clean spacing.
  - `nh3` HTML sanitizer enforced on model `save()` methods and template tag `|sanitize_html`.
- Harmonized Dark Mode (Theme):
  - Recommended Events container (`.recommended-events-box`) and Home Tabs navigation (`.nav-pills-hubs`) feature dark body background, brand teal/green border (`1.5px solid var(--hubs-primary)`, `#2ba1ab`), white text on inactive items, and white counter badges with colored numbers.
- Multi-Device LAN Mobile Testing Support:
  - Dynamic local IP detection in `DEBUG` mode adding host LAN IP to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
  - Vite dev server listening on `0.0.0.0:5173` with dynamic `dev_server_host` in `DJANGO_VITE` for mobile browsers on the same WiFi.
- Layered Rate Limiting & Defense-in-Depth:
  - Nginx perimeter rate limiting (`auth_limit` zone, 5 req/m, burst=3-5 nodelay) over `/login/`, `/register/`, `/password-reset/`, and `/password_reset/`.
  - Nginx API rate limiting (`api_limit` zone, 60 req/m, burst=20 nodelay) across all `/api/` endpoints.
  - Django REST Framework application-level throttling (`AnonRateThrottle` at 60/min, `UserRateThrottle` at 300/min).
- Strict Access Control & Anti-IDOR/BOLA:
  - Chat API: `MessageListView` raises `PermissionDenied("No eres participante de esta conversación")` resulting in explicit HTTP 403 Forbidden for non-members.
  - Channels WebSockets: `ChatConsumer` disconnects immediately on unauthorized connection attempts or non-member socket operations.
  - Domain views: `ArticleUpdateView` and `ArticleDeleteView` in `library`, `PostDeleteView` in `posts`, and event lifecycle routes enforce strict ownership checks with 403 Forbidden.
- Zero-Downtime Secret Rotation:
  - Support for `SECRET_KEY_FALLBACKS` list in `settings.py`, allowing key rotation without terminating existing user sessions or invalidating active tokens.
  - Production defensive validation requiring minimum 32 characters and prohibiting `django-insecure` prefixes.
- Branded & Resilient Error Pages:
  - Custom `404.html` and `403.html` matching corporate branding and extending `layout.html`.
  - Standalone `500.html` with zero database, zero ORM, and zero Django static dependencies, utilizing inline CSS and CDN fallback to render reliably even during database outages.
- Botanical High-Contrast Footer (`.footer-hubs`):
  - Anchored deep botanical forest green (`#16281e` in light theme, `#0c130f` in dark theme) providing visual stability.
  - WCAG AAA contrast compliance across all text tokens (`--hubs-footer-text: #c5d3ca`, brand `#8bd3ab`, titles `#f8faf9`/`#f1f5f2`).
  - Interactive cookie settings modal trigger (`.footer-btn-cookies`) and accessible navigation links.
- Strict 1-Hour Rolling Session Security & Inactivity Expiration:
  - `SESSION_COOKIE_AGE = 3600` (1 hora) y `SESSION_SAVE_EVERY_REQUEST = True` (renovación continua con actividad del usuario).
  - Cierre inmediato al cerrar navegador (`SESSION_EXPIRE_AT_BROWSER_CLOSE = True`) y protección HttpOnly.
  - Expiración estricta tras 60 minutos de inactividad con redirección 302 a `/login/` y revocación de autenticación.
  - Tarea nocturna Celery Beat `clear_expired_sessions_task` diaria a las 03:00 AM ejecutando `clearsessions`.
- Intelligent Domain Resolution & example.com Prevention:
  - Constructor canónico de URLs (`aficionados_network/utils/site.py`) que resuelve jerárquicamente `SITE_DOMAIN`, `SITE_URL` o `ALLOWED_HOSTS` para todos los correos transaccionales, señales de bienvenida (`send_welcome_email_on_activation`) y tareas asíncronas de Celery.
  - Migración de datos `profiles/migrations/0012_update_site_domain.py` y comando de gestión `update_site` desterrando el registro residual `example.com`.
- Automated Marketplace 90-Day Lifecycle & Media Cleanup:
  - Ventana de advertencia previa e idempotente a los 83 días (7 días antes de expirar) con bandera de seguimiento en base de datos (`expiration_warning_sent`).
  - Hard delete definitivo de anuncios a los 90 días ejecutado en Celery Beat a las 04:00 AM (`manage_marketplace_lifecycle_task`).
  - Señal Django `post_delete` en `marketplace/signals.py` que destruye físicamente del almacenamiento (`default_storage.delete()`) los archivos de imagen y video asociados al borrarse un anuncio (por mantenimiento o acción manual del usuario).
- Conservative Ops Maintenance & Proactive Disk Monitoring:
  - Rotación transversal de logs de Docker (`10m` x 3 archivos en los 7 servicios) con un límite estricto de 30 MB por contenedor y 210 MB para todo el clúster.
  - Purga conservadora de notificaciones leídas (`is_read=True`) con más de 90 días a las 03:30 AM en lotes defensivos de 500 registros (chunking) para proteger InnoDB, preservando incondicionalmente las no leídas.
  - Limpieza de archivos temporales huérfanos en `MEDIA_ROOT/temp/` (> 48h) a las 04:30 AM con verificación de límites de ruta.
  - Monitor proactivo de disco en Celery Beat a las 05:00 AM con alerta por correo electrónico a todos los superusuarios activos (y fallback a `settings.ADMINS`) ante umbrales de WARNING (>= 75%) y CRITICAL (>= 90%).


## Runtime & Infrastructure

Stack:

- **Python:** 3.12.
- **Django:** 6.0.
- **ASGI / WebSockets:** Django Channels 4.2+ running under Daphne.
- **Database:**
  - MariaDB 10.11 in production with charset `utf8mb4` and `COLLATE utf8mb4_unicode_ci`.
  - SQLite 3 in development and fast in-memory test executions (`DB_ENGINE=sqlite`).
  - PyMySQL fallback configured for pure-Python database compatibility.
- **Cache & Broker:** Redis 7 Alpine.
- **Asynchronous Tasks:** Celery 5.7+ Worker (`celery_worker` service in Docker Compose).
- **Periodic Scheduler:** Celery Beat (`celery_beat` service in Docker Compose) orquestando el cronograma nocturno completo de mantenimiento y recordatorios matutinos:

  | Horario (UTC) | Tarea | Propósito / Características |
  | :--- | :--- | :--- |
  | **03:00 AM** | `aficionados_network.tasks.clear_expired_sessions_task` | Limpieza de sesiones expiradas en `django_session` vía `clearsessions` con autoretry. |
  | **03:30 AM** | `notifications.tasks.clean_old_read_notifications_task` | Purga conservadora de notificaciones leídas (`is_read=True`) > 90 días en lotes de 500 registros para proteger InnoDB. Preserva no leídas. |
  | **04:00 AM** | `marketplace.tasks.manage_marketplace_lifecycle_task` | Ciclo de vida del mercadillo: aviso a vendedores a los 83 días (idempotente) y hard delete a los 90 días con borrado físico de fotos y videos. |
  | **04:30 AM** | `aficionados_network.tasks.clean_temp_media_files_task` | Limpieza defensiva de archivos temporales huérfanos en `MEDIA_ROOT/temp/` con más de 48h de antigüedad. |
  | **05:00 AM** | `aficionados_network.tasks.check_disk_usage_task` | Monitor de uso de disco en el sistema de archivos con despacho automático de correos a superusuarios ante umbrales del 75% (Warning) y 90% (Critical). |
  | **08:00 AM** | `posts.tasks.send_event_reminders_task` | Despacho de recordatorios 24h para eventos futuros con idempotencia multinivel (`reminder_sent`). |

- **Reverse Proxy & Edge:**
  - Nginx 1.25 Alpine with layered rate limiting (`auth_limit` zone for auth routes and `api_limit` zone for `/api/`), HSTS, CSP `sandbox` on `/media/`, internal `/protected_media/` via `X-Accel-Redirect`, and ACME webroot challenge routing (`/.well-known/acme-challenge/`).
  - Ports exposed: `80`, `8000`, and `443` (prepared for HTTPS).
- **SSL / TLS Provisioning:**
  - Official Certbot service in Docker Compose running background renewal checks every 12h.
  - Zero-downtime transition architecture using shared ACME webroot volume (`certbot_www`) and production template (`nginx/production-ssl.conf.template`).
  - Operational runbook: `docs/runbook-ssl.md`.
- **Frontend Chat Module:**
  - React 19, Vite 8, TypeScript 5+.
  - 100% TypeScript compliance verified via `npm run type-check` (`tsc --noEmit`).
  - Container-Presentational separation and Anti-Corruption Layer (`httpClient.ts`, `chat.service.ts`, `chat.types.ts`).

Docker Compose Services:
- `web`: Django 6.0 + Daphne ASGI (`env_file: .env.prod`, depends on `db`, `redis`).
- `db`: MariaDB 10.11 (`volume: db_data`).
- `redis`: Redis 7 Alpine.
- `celery_worker`: `celery -A aficionados_network worker -l info --concurrency=2`.
- `celery_beat`: `celery -A aficionados_network beat -l info`.
- `nginx`: Nginx 1.25 Alpine (`ports: 80, 8000, 443`, depends on `web`).
- `certbot`: `certbot/certbot:latest` daemon with shared volumes `certbot_www` and `certbot_conf`.

*Política de Rotación de Logs de Docker:* Los 7 servicios integran rotación estricta de logs con driver `json-file` (`max-size: "10m"`, `max-file: "3"`), limitando el espacio de logs a un máximo absoluto de 30 MB por contenedor y 210 MB para todo el clúster.

Operational command for tests:

```bash
# Backend unit & integration test suite (173 tests)
DB_ENGINE=sqlite ./env/bin/python manage.py test

# Frontend TypeScript type check (0 errors)
cd frontend && npm run type-check
```

Last known verification:

```text
Ran 173 tests in ~5.0s (100% GREEN)
Frontend type-check: 0 errors (tsc --noEmit clean)
```


## Source Layout

Main project package and app:

- `aficionados_network/celery.py`: Celery app initialization, beat schedule definition (staggered nightly maintenance tasks 03:00-05:00 AM and `send_event_reminders_task` daily at 08:00 AM), and task discovery.
- `aficionados_network/tasks.py`: Asynchronous tasks (`send_email_task` with exponential backoff and jitter), and maintenance tasks: `clear_expired_sessions_task` (03:00 AM), `clean_temp_media_files_task` (04:30 AM), `check_disk_usage_task` (05:00 AM with active email dispatch to superusers at >= 75% and >= 90%).
- `aficionados_network/utils/site.py`: Intelligent site domain resolution, base URL calculation, and canonical absolute URL construction (`build_absolute_url`, `get_site_domain`, `get_site_protocol`, `get_base_url`).
- `aficionados_network/utils/mailer.py`: Resilient email dispatch helper (Celery primary, ThreadPool fallback, template rendering with extra context).
- `aficionados_network/utils/sanitizer.py`: `nh3` HTML sanitizer with strict tag/attribute allowlists and automatic `rel="noopener noreferrer"`.
- `aficionados_network/settings.py`: settings, env handling (`SITE_DOMAIN`, `SITE_URL`, `SITE_NAME`, `SITE_PROTOCOL`), DB selector, static/media/email, test profiling (InMemoryChannelLayer, MD5PasswordHasher, CompressedStaticFilesStorage, CELERY_TASK_ALWAYS_EAGER), `SECRET_KEY_FALLBACKS` support with defensive validation, and REST_FRAMEWORK throttling (`AnonRateThrottle`, `UserRateThrottle`).
- `aficionados_network/urls.py`: root URL dispatcher.
- `aficionados_network/views.py`: home, auth, registration activation, contact form (with safe reply-to).
- `aficionados_network/models.py`: `ContactMessage`.
- `aficionados_network/forms.py`: auth/profile/contact/hobby forms.
- `aficionados_network/templates/`: main shared template tree, including custom error pages (`404.html`, `403.html`, and standalone `500.html`) and redesigned botanical footer (`_includes/_footer.html`).

Domain apps:

- `profiles/`: profiles, hobbies, follows, reviews, profile routes, profile signals (`send_welcome_email_on_activation` with canonical URL resolution).
  - `profiles/templates/profiles/profile_edit.html`: Profile editing with TinyMCE bio and TomSelect searchable hobby selector.
  - `profiles/management/commands/update_site.py`: Management command to update site domain and name in `django.contrib.sites`.
  - Recent migrations: `0011_alter_hobby_options`, `0012_update_site_domain` (purges default `example.com`).
- `posts/`: Clicks, comments, Eventos, event comments, event routes, likes, attendance, hub/gallery flows.
  - `posts/tasks.py`: `send_event_reminders_task` with multi-level idempotency and atomic transactions (scheduled at 08:00 AM).
  - Recent migration: `0023_eventattendance_reminder_sent_and_more` (adds `reminder_sent`, `reminder_sent_at`, and compound index).
- `notifications/`: notification model, follow signal, unread context, list and redirect routes.
  - `notifications/services.py`: `NotificationDispatcher` centralizing dispatch for all business domains.
  - `notifications/tasks.py`: `clean_old_read_notifications_task` running at 03:30 AM with 500-record chunking to protect InnoDB while preserving unread notifications.
  - Recent migrations: `0007_notification_article_and_more`, `0008_alter_notification_notification_type`.
- `chat/`: Models (`Conversation`, `Message`, `GroupJoinRequest`), DRF API views, Channels WebSockets consumers, protected attachment endpoints (`ProtectedAttachmentDownloadView`), and magic bytes / EXIF validation.
- `gamification/`: Badges, levels, and user progression calculations with `O(1)` caching and direct database aggregations.
- `marketplace/`: Listings, categories, and marketplace interactions with open-redirect mitigation.
  - `marketplace/signals.py`: `post_delete` signal listener physically destroying associated `image` and `video` files upon listing deletion.
  - `marketplace/tasks.py`: `manage_marketplace_lifecycle_task` scheduled daily at 04:00 AM.
  - `marketplace/management/commands/manage_marketplace_lifecycle.py`: Lifecycle management command with `--dry-run` flag, 83-90 day warning window, and 90-day hard delete.
  - Recent migration: `0005_listing_expiration_warning_sent` (tracks courtesy notification state).
- `library/`: Articles, clinical cases, and knowledge repository with TinyMCE and HTML entity sanitization.

Frontend module:

- `frontend/src/ChatApp.tsx`: Root React container for chat.
- `frontend/src/components/chat/`:
  - `MessageArea.tsx`: Smart container coordinating active conversation state.
  - `MessageTimeline.tsx`: Presentational component for messages, bubbles, and custom document cards.
  - `MessageInput.tsx`: Presentational input bar with microphone recording and file upload.
  - `AttachmentPreview.tsx`: Presentational file preview with color-coded type badges.
  - `GroupParticipants.tsx`, `GroupPendingRequests.tsx`, `GroupAddMember.tsx`: Modal presentational components.
- `frontend/src/api/httpClient.ts`: Anti-Corruption Layer wrapping axios with CSRF token extraction and header injection.
- `frontend/src/api/chat.service.ts`: Domain service methods decoupling UI from REST endpoints.
- `frontend/src/types/chat.types.ts`: Strict TypeScript interfaces for messages, users, conversations, and attachments.
- `frontend/src/hooks/useWebSocket.ts`: Strictly typed WebSocket connection hook with reconnect and heartbeat handling.
- `frontend/src/hooks/useChatRecorder.ts`: Audio recorder hook wrapping browser MediaRecorder.

Infrastructure & Ops:

- `docker-compose.yml`: Multi-container production topology (web, db, redis, celery_worker, celery_beat, nginx, certbot) with strict log rotation policy (`max-size: "10m"`, `max-file: "3"` across all 7 services).
- `nginx/default.conf`: Current active Nginx configuration with Rate Limiting, `X-Accel-Redirect`, and ACME webroot routing.
- `nginx/production-ssl.conf.template`: Declarative SSL/TLS configuration template for production deployment with `envsubst`.
- `docs/runbook-ssl.md`: Step-by-step Zero-Downtime SSL deployment runbook.


## Active Truths

- The app is server-rendered Django, with an embedded React 19 chat module in strict TypeScript.
- Site domain resolution is managed via `aficionados_network/utils/site.py`, driven by `SITE_DOMAIN`, `SITE_URL`, `SITE_NAME`, and `SITE_PROTOCOL`, ensuring zero `example.com` leakage in transactional emails and tasks.
- Session security enforces a 1-hour rolling timeout (`SESSION_COOKIE_AGE = 3600`, `SESSION_SAVE_EVERY_REQUEST = True`), expiring at browser close and cleaned nightly by Celery Beat at 03:00 AM (`clear_expired_sessions_task`).
- Celery Beat coordinates a 6-phase schedule: 03:00 AM sessions, 03:30 AM read notifications (chunking 500), 04:00 AM marketplace lifecycle, 04:30 AM temp media, 05:00 AM disk monitoring, and 08:00 AM event reminders.
- Marketplace listings follow a strict 90-day lifecycle: sellers receive an idempotent warning at 83 days (`expiration_warning_sent=True`), listings > 90 days undergo hard delete, and physical media is immediately deleted from disk via `post_delete` signal.
- Docker containers in `docker-compose.yml` enforce a strict `10m` x 3 log rotation policy, preventing host disk saturation.
- `posts` owns both social posts and event workflows, as well as the 24h event reminder task (`posts.tasks.send_event_reminders_task`).
- `profiles.Hobby` is the shared category model for posts, events, and user interests.
- `profiles.UserHobby` stores a user's level per hobby and powers match/mentor logic.
- `notifications.services.NotificationDispatcher` is the single source of truth for all business notifications (in-app + async emails).
- In-app notifications and emails are both product behavior; preserve both when changing interactions.
- `profiles.signals` creates profiles for new non-superuser users and triggers welcome notifications via `NotificationDispatcher`.
- In test mode (`TESTING = 'test' in sys.argv`), Celery is eager (`CELERY_TASK_ALWAYS_EAGER = True`), channel layer is in-memory (`InMemoryChannelLayer`), password hashing uses MD5 (`MD5PasswordHasher`), and static storage skips strict manifest checks (`CompressedStaticFilesStorage`).


## Verified Coverage

Tests currently cover 173 test cases across:

- Core pages, auth, registration activation, contact email, Celery email dispatch.
- Site and domain canonical resolution + activation emails without example.com (`test_site_and_activation_email.py`).
- Session security, 1-hour rolling timeout, 60min inactivity expiration redirect, and Celery Beat clearsessions (`test_session_timeout.py`).
- Profile model behavior, follows, hobbies, reviews, and anti-self-review authorization.
- Profile routes and follow notifications.
- Post model behavior, likes, comments, emails, modal partial, and deletion authorization.
- Event lifecycle: create, attend, cancel, reactivate, duplicate, comment, and organizer authorization checks.
- Event reminders: Celery Beat task execution, 24h window filtering, multi-level idempotency (`reminder_sent`), atomic transactions, unconfirmed user exclusion, and error handling.
- Marketplace lifecycle: 83-day warning idempotency, 90-day hard delete, physical file deletion via post_delete signal, `--dry-run` flag, and Celery task (`test_lifecycle.py`).
- Maintenance tasks: notification purge chunking (500), temp media cleanup (> 48h), disk monitor, and proactive email alerts to superusers (75% / 90%) (`test_tasks.py`, `test_maintenance_tasks.py`).
- NotificationDispatcher service: in-app creation, email dispatch, Celery resilience, template fallback, and all business event types.
- Hobby hub and clicks gallery smoke behavior.
- Notification list, unread count, redirects, context processor.
- Chat APIs: explicit `HTTP 403 Forbidden` rejection for non-participants querying messages, conversation isolation, protected attachment downloads (`X-Accel-Redirect`), and WebSockets security with disconnection for non-participants/unauthenticated sockets (`AllowedHostsOriginValidator`).
- Library article comments and ratings notification dispatch, plus strict `403 Forbidden` authorization verification for unauthorized edits and deletions (`ArticleUpdateView`, `ArticleDeleteView`).
- Gamification scoring and badges with `O(1)` check and database aggregations.
- Marketplace listing creation and filters.
- Frontend: Strict TypeScript compilation passing with 0 errors via `npm run type-check`.


## Known Caveats

- `aficionados_network/views.py` contains duplicated/legacy profile classes; current root URLs use `profiles.views` for active profile list/detail.
- `HomeView` is defined twice in `aficionados_network/views.py`; the second definition is effective.
- Profile routes exist both as global routes and namespaced routes; check templates before renaming.
- `notifications/context_procesors.py` is a misspelled duplicate-like file; settings use `notifications.context_processors`.
- `posts.Posts.save()` contains unrelated self-follow validation logic that appears historical.
- `EventComment` is not registered in `posts/admin.py`.
- Match/mentor flags such as `is_match` and `is_mentor` are runtime attributes assigned in views, not model fields.
- Uploaded media paths live in the DB, but actual files live under `media/`.


## Before Changing Code

Read these in order:

1. `index.md`
2. `current-state.md`
3. `architecture-map.md`
4. `decision-log.md`
5. Domain-specific knowledge docs under `knowledge/`
6. `docs/runbook-ssl.md` before any infrastructure or perimeter change.

Before finishing code work:

- Run the test suite: `./env/bin/python manage.py test`.
- Run frontend type check: `cd frontend && npm run type-check`.
- Add or update tests for changed behavior.
- Update `changelog-logical.md` for semantic changes.
- Update `current-state.md` if operational truth changed.
- Add a decision to `decision-log.md` if a meaningful technical choice was made.
