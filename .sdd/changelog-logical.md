# Logical Changelog

**Last reviewed:** 2026-06-01  
**Purpose:** semantic change history of the system, independent from Git commits.

This log records meaningful product/architecture/testing changes. Use it to understand how the system evolved and what behavior changed.

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
