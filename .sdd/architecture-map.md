# Architecture Map

**Last reviewed:** 2026-11-27  
**Purpose:** compact map of modules, responsibilities, and relationships.

## System Shape

Hubs&Clicks is a Django monolith with multiple apps:

```text
Browser
  -> Django URL routing
  -> Views / forms
  -> Models / signals
  -> Templates / static assets
  -> Database + media filesystem + email backend
```

The application uses server-rendered pages as the primary experience. JavaScript/AJAX/HTMX-style responses enhance likes, comments, galleries, hubs, cookie behavior, and partial rendering.

## Apps And Responsibilities

### `aficionados_network`

Two roles:

- Django project package: settings, root URLs, ASGI/WSGI.
- General app: home, auth, registration pending, contact messages.

Key files:

- `settings.py`: env loading, apps, middleware, DB selection, static/media/email/security.
- `urls.py`: top-level routing.
- `views.py`: home, login/logout/register/contact, plus legacy profile views.
- `models.py`: `ContactMessage`.
- `forms.py`: register/login/user/profile/contact/add-hobby forms.
- `templates/`: main global template tree.

Relations:

- Reads `posts.Posts`, `posts.Event`, `profiles.Follow`, `profiles.UserHobby`, `profiles.Hobby`.
- Sends registration, welcome, and contact emails.

### `profiles`

Owns user social identity and reputation.

Key models:

- `Hobby`
- `UserProfile`
- `UserHobby`
- `Follow`
- `Review`

Key flows:

- Automatic profile creation.
- Profile display/edit.
- Hobby membership and levels.
- Follow/unfollow.
- Organizer reviews after event participation.

Relations:

- Extends Django `User` through `UserProfile`.
- Shared `Hobby` is consumed by posts and events.
- `Review` points to `posts.Event`.
- Follow creation triggers notifications.

### `posts`

Owns both content posts and event workflows.

Key models:

- `Posts`
- `Comment`
- `Event`
- `EventComment`

Key flows:

- Create/edit/delete Clicks.
- Like posts.
- Comment on posts.
- Create/list/detail/edit/cancel/reactivate/duplicate events.
- Join/leave events.
- Comment on events.
- List personal participations and owned events.
- Hobby hub and clicks gallery.

Relations:

- `Posts.category -> profiles.Hobby`.
- `Event.hobby -> profiles.Hobby`.
- `Event.organizer -> User`.
- `Event.participants -> User`.
- Creates `notifications.Notification` rows.
- Sends branded emails for comments and event interactions.

### `notifications`

Owns in-app notification persistence and navigation.

Key model:

- `Notification`

Key flows:

- Follow notification signal.
- Notification list.
- Unread count context and endpoint.
- Smart redirect to post, event, profile, or fallback list.
- `clean_old_read_notifications_task`: Nocturnal conservative purge (03:30 AM) of read notifications (> 90 days) in 500-record chunks.

Relations:

- Links to `User`, `posts.Posts`, `posts.Comment`, `posts.Event`, and `profiles.Review`.
- Context processor is globally available to templates.

### `marketplace`

Owns therapeutic equipment, room rentals, and professional services exchange.

Key model:

- `Listing` (with `expiration_warning_sent` boolean tracker).

Key flows:

- Marketplace listing creation, detail, edit, search, and category filtering.
- Seller reviews and 1-on-1 private chat integration.
- 90-Day Lifecycle Automation (`manage_marketplace_lifecycle_task` daily at 04:00 AM):
  * Idempotent warning email to seller at 83 days (7 days before expiration).
  * Automated hard delete at 90 days.
  * Physical media cleanup: `post_delete` signal destroys associated image and video files from disk storage.

Relations:

- `Listing.seller -> auth.User`.
- `Listing.category -> profiles.Hobby`.
- Connects to `chat.Conversation` for private transactions.

## Core Model Relationships

```text
auth.User
  1--1 profiles.UserProfile
  1--N posts.Posts
  1--N posts.Event as organizer
  N--N posts.Event as participants
  N--N posts.Posts as likes
  1--N notifications.Notification as recipient/sender

profiles.UserProfile
  N--N profiles.UserProfile through profiles.Follow
  N--N profiles.Hobby through profiles.UserHobby

profiles.Hobby
  1--N profiles.UserHobby
  1--N posts.Posts
  1--N posts.Event

posts.Posts
  1--N posts.Comment
  N--N auth.User as likes

posts.Event
  1--N posts.EventComment
  N--N auth.User as participants
  1--N profiles.Review

notifications.Notification
  optional -> posts.Posts
  optional -> posts.Comment
  optional -> posts.Event
  optional -> profiles.Review
```

## Route Map

Root routes in `aficionados_network/urls.py`:

- `/`: home.
- `/admin/`: admin.
- `/events/`: includes `posts.urls`.
- `/profile/`: includes `profiles.urls`.
- `/profile/list/`: profile list shortcut.
- `/profile/<pk>/`: profile detail shortcut.
- `/login/`, `/logout/`, `/register/`: auth/registration.
- `/password-reset/...`: password reset.
- `/contact/`: contact form.
- `/legal/`, `/privacidad/`, `/politica-cookies/`, `/cookies/`: legal/static pages.
- `/pages/`: flatpages.
- `/notifications/`: includes `notifications.urls`.

Posts/events routes under `/events/`:

- event list/detail/create/edit/cancel/reactivate/duplicate.
- attendance toggle.
- event comments.
- post create/detail/edit/delete.
- post like/comment.
- hobby hub and hobby membership toggle.
- my participations, my organized plans, clicks gallery.

Profiles routes under `/profile/`:

- profile list/detail/edit.
- add/delete hobby.
- add review.

Notifications routes under `/notifications/`:

- list.
- read/redirect.
- unread count endpoint.

## Template Map

Global shell:

- `general/layout.html`
- `_includes/_header.html`
- `_includes/_footer.html`
- `_includes/_messages.html`
- `_includes/_cookies_banner.html`

Main domain templates:

- `general/home.html`
- `general/login.html`
- `general/register.html`
- `general/contact.html`
- `posts/event_*`
- `posts/post_*`
- `posts/hobby_hub.html`
- `posts/clicks_list.html`
- `posts/partials/*`
- `profiles/templates/profiles/*`
- `notifications/list.html`
- `registration/*`
- `general/emails/notification_email.html`

## Static And Media

Static:

- CSS: `static/css/style.css`.
- JS: `forms.js`, `community-hub.js`, `cookies.js`, `ajax-hubs.js`, `likes.js`, `comentarios.js`.
- Images/logos: `logo_hubs.png`, `logo_hubs_email.png`, default profile/event images.

Media:

- User-uploaded files under `media/`.
- DB stores file paths.
- Media backup/copy is separate from DB migration.

## Cross-Cutting Flows

### Registration

`RegisterView` creates inactive user -> user sees 72h pending screen -> Admin manually marks `is_active=True` in Django Admin -> Signal sends welcome email.

### Home Personalization

Home reads follows, posts, user hobbies, user levels, and upcoming events. It computes match counts and runtime event tags.

### Event Matching

`UserHobby.level` is compared against `Event.level`. `all` matches everyone. A user with a higher level can be marked as mentor in some views.

### Notifications

Interactions create `Notification` rows. The header can display unread count through context processor/API. Clicking notifications marks them read and redirects to relevant content.

### Emails

Important interactions use branded HTML email templates and CID logos. Dynamic absolute URL resolution is orchestrated via `aficionados_network/utils/site.py` (`SITE_DOMAIN`, `SITE_URL`) preventing `example.com` in email links. Tests use locmem email backend.

### Nocturnal Maintenance & Proactive Infrastructure Monitoring (Celery Beat)

Staggered automated maintenance executed daily in production:
- 03:00 AM: `clear_expired_sessions_task` (purges expired Django sessions via `clearsessions`).
- 03:30 AM: `clean_old_read_notifications_task` (conservative purge of read notifications > 90d in 500-record chunks to protect InnoDB).
- 04:00 AM: `manage_marketplace_lifecycle_task` (83d warning, 90d hard delete + physical media removal).
- 04:30 AM: `clean_temp_media_files_task` (removes orphaned `media/temp/` files > 48h).
- 05:00 AM: `check_disk_usage_task` (monitors disk space and sends proactive alert emails to superusers at >= 75% and >= 90%).
- 08:00 AM: `send_event_reminders_task` (24h event reminders with strict idempotency).

## Areas To Handle Carefully

- Profile route duplication/global vs namespaced names.
- Legacy profile code inside `aficionados_network/views.py`.
- Signal behavior during fixture loading.
- Runtime-only attributes such as `is_match`.
- Upload cleanup and media paths.
- Email template paths and domain canonical resolution.
- MySQL vs SQLite behavior.
- **Soft Delete vs. Hard Delete Patterns**:
  * Core social models (`Posts`, `Event`, `Hobby`) inherit from `SoftDeleteModel` (flagging `is_active=False` with `PROTECT` on foreign keys).
  * `Marketplace.Listing` uses a scheduled **Hard Delete** at 90 days with physical storage file cleanup via `post_delete` signal to prevent storage bloating.
