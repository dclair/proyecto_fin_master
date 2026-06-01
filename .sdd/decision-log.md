# Decision Log

**Last reviewed:** 2026-06-01  
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
