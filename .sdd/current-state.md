# Current State

**Last reviewed:** 2026-09-03  
**Role:** single operational truth for the project today.

This document is the first place to check before modifying Hubs&Clicks. It summarizes what is currently true, what is verified, what is risky, and where deeper details live.

## Product

Hubs&Clicks is a Django social network for connecting people through hobbies and natural therapies.

Current user-facing capabilities:

- Register, activate account by email, log in, and log out.
- Edit profile data: avatar, bio, birth date, location, website, identity fields.
- Add hobbies to profile with experience levels.
- Follow and unfollow other profiles.
- Create multi-content posts (Clicks): combines non-exclusive photo, video, generic external link, and attached PDF document (up to 10MB).
- Explore all community posts (`/events/posts/`) with keyword search, therapy filter, clean server-side pagination (12 per page), and symmetric Home button.
- Like and comment on posts.
- Create hobby-based events with TinyMCE rich descriptions and TomSelect searchable category dropdowns sorted alphabetically.
- Join or leave events when allowed.
- Cancel, reactivate, duplicate, edit, and list owned events.
- View personal event participations.
- Support for Hybrid events (Physical/Online) with physical capacity limits.
- Browse the "Comunidad de Terapeutas" (Therapists Community) with infinite scrolling (HTMX) and multi-field search (username, name, email).
- Review event organizers after participation with a 5-star system.
- Receive in-app notifications.
- Receive HTML emails for important interactions.
- Send contact messages to the site owner/admin.
- Chat in real-time (1-on-1 and Groups) with multimedia support (images, videos, documents).
- Full control over messages ("Delete for everyone" and "Delete for me").
- Filter events easily matching the user's registered therapies ("Mis Terapias" filter).
- Upload local images directly into the biography editor via TinyMCE integration.
- Official Institutional Channel "Ágora" (`slug="agora"`):
  - Automatically assigned to all new users upon registration as their default primary therapy.
  - Existing users retroactively assigned via migration `0010_assign_agora_to_all_profiles`.
  - Publishing strictly restricted to `is_staff` users (superusers, admins, board members).
  - High-visibility orange badge (`.badge-agora` / `.badge-agora-solid`, `#ea580c`) with official shield icon.
  - Priority pinned to first position (index 0) in Home feeds (Posts, Events, Library) via ORM `Case/When` annotation (`is_agora`).
- Universal Plain-Text Extraction & HTML Entity Sanitization:
  - Properties `Article.plain_text_summary`, `Posts.plain_text_caption`, and `Event.plain_text_description` decode HTML entities (`&eacute;` -> `é`, `&nbsp;` -> ` `) and separate block tags with clean spacing.
- Harmonized Dark Mode (Theme):
  - Recommended Events container (`.recommended-events-box`) and Home Tabs navigation (`.nav-pills-hubs`) feature dark body background, brand teal/green border (`1.5px solid var(--hubs-primary)`, `#2ba1ab`), white text on inactive items, and white counter badges with colored numbers.


## Runtime

Stack:

- Python 3.12 intended.
- Django 6.0.
- Bootstrap/crispy forms for server-rendered UI.
- Vanilla JS, AJAX, and some HTMX-style partial responses.
- React 18 embedded via Vite for the Chat interface.
- Django Channels for WebSockets (ASGI).
- Pillow for image handling.
- Django email with HTML templates and CID logos.

Database:

- Environment-selected in `aficionados_network/settings.py`.
- `DB_ENGINE=sqlite` uses `db.sqlite3`.
- `DB_ENGINE=mysql` or `mariadb` uses MySQL/MariaDB with PyMySQL fallback.
- Current local `.env` may select MySQL by default.
- SQLite remains the recommended local test backend.

Operational command for tests:

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py test --verbosity 1
```

Last known verification:

```text
35 tests passing with SQLite
```

## Source Layout

Main project package and app:

- `aficionados_network/settings.py`: settings, env handling, DB selector, static/media/email.
- `aficionados_network/urls.py`: root URL dispatcher.
- `aficionados_network/views.py`: home, auth, registration activation, contact form, legacy profile code.
- `aficionados_network/models.py`: `ContactMessage`.
- `aficionados_network/forms.py`: auth/profile/contact/hobby forms.
- `aficionados_network/templates/`: main shared template tree.

Domain apps:

- `profiles/`: profiles, hobbies, follows, reviews, profile routes, profile signals.
- `posts/`: Clicks, comments, Eventos, event comments, event routes, likes, attendance, hub/gallery flows.
- `notifications/`: notification model, follow signal, unread context, list and redirect routes.
- `chat/`: Models (`Conversation`, `Message`, `GroupJoinRequest`), DRF API views, and Channels WebSockets consumers.

Assets and data:

- `static/`: CSS, JS, logos, default images.
- `media/`: uploaded user files. Back up separately from database.
- `db.sqlite3`, `db.sqlite3.backup`, `db_full_backup.json`: local/operational database artifacts.

## Active Truths

- The app is server-rendered Django, not a SPA.
- `posts` owns both social posts and event workflows.
- `profiles.Hobby` is the shared category model for posts, events, and user interests.
- `profiles.UserHobby` stores a user's level per hobby and powers match/mentor logic.
- `notifications.Notification` is generic and can point to a post, event, comment, or review.
- In-app notifications and emails are both product behavior; preserve both when changing interactions.
- `profiles.signals` creates profiles for new non-superuser users.
- `notifications.signals` creates follow notifications and is fixture-safe with `raw=True`.
- Contact email template path was corrected to `general/emails/notification_email.html` on 2026-06-01.

## Verified Coverage

Tests currently cover:

- Core pages, auth, registration activation, contact email.
- Profile model behavior, follows, hobbies, reviews.
- Profile routes and follow notifications.
- Post model behavior, likes, comments, emails, modal partial.
- Event lifecycle: create, attend, cancel, reactivate, duplicate, comment.
- Hobby hub and clicks gallery smoke behavior.
- Notification list, unread count, redirects, context processor.

For details, read `knowledge/testing-strategy-hubs-clicks.md`.

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

Before finishing code work:

- Run the SQLite test command above.
- Add or update tests for changed behavior.
- Update `changelog-logical.md` for semantic changes.
- Update `current-state.md` if operational truth changed.
- Add a decision to `decision-log.md` if a meaningful technical choice was made.
