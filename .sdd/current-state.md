# Current State

**Last reviewed:** 2026-11-24  
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
- Edit profile data: avatar, bio (with TinyMCE rich text and local image upload), birth date, location, website, identity fields.
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
- **Periodic Scheduler:** Celery Beat (`celery_beat` service in Docker Compose).
- **Reverse Proxy & Edge:**
  - Nginx 1.25 Alpine with rate limiting (`limit_req_zone`), HSTS, CSP `sandbox` on `/media/`, internal `/protected_media/` via `X-Accel-Redirect`, and ACME webroot challenge routing (`/.well-known/acme-challenge/`).
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

Operational command for tests:

```bash
# Backend unit & integration test suite (129 tests)
DB_ENGINE=sqlite ./env/bin/python manage.py test

# Frontend TypeScript type check (0 errors)
cd frontend && npm run type-check
```

Last known verification:

```text
Ran 129 tests in ~4.5s (100% GREEN)
Frontend type-check: 0 errors (tsc --noEmit clean)
```


## Source Layout

Main project package and app:

- `aficionados_network/celery.py`: Celery app initialization, beat schedule definition (`posts.tasks.send_event_reminders_task` daily at 8:00 AM), and task discovery.
- `aficionados_network/tasks.py`: Asynchronous tasks (`send_email_task` with exponential backoff and jitter).
- `aficionados_network/utils/mailer.py`: Resilient email dispatch helper (Celery primary, ThreadPool fallback, template rendering with extra context).
- `aficionados_network/utils/sanitizer.py`: `nh3` HTML sanitizer with strict tag/attribute allowlists and automatic `rel="noopener noreferrer"`.
- `aficionados_network/settings.py`: settings, env handling, DB selector, static/media/email, test profiling (InMemoryChannelLayer, MD5PasswordHasher, CompressedStaticFilesStorage, CELERY_TASK_ALWAYS_EAGER).
- `aficionados_network/urls.py`: root URL dispatcher.
- `aficionados_network/views.py`: home, auth, registration activation, contact form (with safe reply-to).
- `aficionados_network/models.py`: `ContactMessage`.
- `aficionados_network/forms.py`: auth/profile/contact/hobby forms.
- `aficionados_network/templates/`: main shared template tree.

Domain apps:

- `profiles/`: profiles, hobbies, follows, reviews, profile routes, profile signals.
  - Recent migration: `0011_alter_hobby_options`.
- `posts/`: Clicks, comments, Eventos, event comments, event routes, likes, attendance, hub/gallery flows.
  - `posts/tasks.py`: `send_event_reminders_task` with multi-level idempotency and atomic transactions.
  - Recent migration: `0023_eventattendance_reminder_sent_and_more` (adds `reminder_sent`, `reminder_sent_at`, and compound index).
- `notifications/`: notification model, follow signal, unread context, list and redirect routes.
  - `notifications/services.py`: `NotificationDispatcher` centralizing dispatch for all business domains.
  - Recent migrations: `0007_notification_article_and_more`, `0008_alter_notification_notification_type`.
- `chat/`: Models (`Conversation`, `Message`, `GroupJoinRequest`), DRF API views, Channels WebSockets consumers, protected attachment endpoints (`ProtectedAttachmentDownloadView`), and magic bytes / EXIF validation.
- `gamification/`: Badges, levels, and user progression calculations with `O(1)` caching and direct database aggregations.
- `marketplace/`: Listings, categories, and marketplace interactions with open-redirect mitigation.
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

- `docker-compose.yml`: Multi-container production topology (web, db, redis, celery_worker, celery_beat, nginx, certbot).
- `nginx/default.conf`: Current active Nginx configuration with Rate Limiting, `X-Accel-Redirect`, and ACME webroot routing.
- `nginx/production-ssl.conf.template`: Declarative SSL/TLS configuration template for production deployment with `envsubst`.
- `docs/runbook-ssl.md`: Step-by-step Zero-Downtime SSL deployment runbook.


## Active Truths

- The app is server-rendered Django, with an embedded React 19 chat module in strict TypeScript.
- `posts` owns both social posts and event workflows, as well as the 24h event reminder task (`posts.tasks.send_event_reminders_task`).
- `profiles.Hobby` is the shared category model for posts, events, and user interests.
- `profiles.UserHobby` stores a user's level per hobby and powers match/mentor logic.
- `notifications.services.NotificationDispatcher` is the single source of truth for all business notifications (in-app + async emails).
- In-app notifications and emails are both product behavior; preserve both when changing interactions.
- `profiles.signals` creates profiles for new non-superuser users and triggers welcome notifications via `NotificationDispatcher`.
- In test mode (`TESTING = 'test' in sys.argv`), Celery is eager (`CELERY_TASK_ALWAYS_EAGER = True`), channel layer is in-memory (`InMemoryChannelLayer`), password hashing uses MD5 (`MD5PasswordHasher`), and static storage skips strict manifest checks (`CompressedStaticFilesStorage`).


## Verified Coverage

Tests currently cover 126 test cases across:

- Core pages, auth, registration activation, contact email, Celery email dispatch.
- Profile model behavior, follows, hobbies, reviews, and anti-self-review authorization.
- Profile routes and follow notifications.
- Post model behavior, likes, comments, emails, modal partial.
- Event lifecycle: create, attend, cancel, reactivate, duplicate, comment.
- Event reminders: Celery Beat task execution, 24h window filtering, multi-level idempotency (`reminder_sent`), atomic transactions, unconfirmed user exclusion, and error handling.
- NotificationDispatcher service: in-app creation, email dispatch, Celery resilience, template fallback, and all business event types.
- Hobby hub and clicks gallery smoke behavior.
- Notification list, unread count, redirects, context processor.
- Chat APIs, conversation isolation, protected attachment downloads (`X-Accel-Redirect`), and WebSockets security (`AllowedHostsOriginValidator`).
- Gamification scoring and badges with `O(1)` check and database aggregations.
- Marketplace listing creation and filters.
- Library article comments and ratings notification dispatch.
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
