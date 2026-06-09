# Logical Changelog

**Last reviewed:** 2026-06-01  
**Purpose:** semantic change history of the system, independent from Git commits.

This log records meaningful product/architecture/testing changes. Use it to understand how the system evolved and what behavior changed.

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
- Quedadas/events.
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
