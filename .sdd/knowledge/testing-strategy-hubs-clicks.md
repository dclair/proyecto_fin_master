# Knowledge Base: Hubs&Clicks Testing Strategy

**Created:** 2026-06-01  
**Status:** Active baseline  
**Current verification:** 35 tests passing with SQLite.

This document records the unit/integration test work added to reduce repeated manual testing of profiles, posts, events, notifications, signals, and emails.

## 1. Command To Run The Suite

Use this as the default local command:

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py test --verbosity 1
```

Last verified result:

```text
Ran 35 tests in 28.819s
OK
```

Why SQLite is the default for tests:

- The project `.env` may point at MySQL/MariaDB.
- The current sandbox blocks local MySQL sockets.
- SQLite test databases are fast, isolated, and enough for normal unit/route coverage.

Use MySQL/MariaDB testing only when validating database-specific behavior:

```bash
env DB_ENGINE=mysql DEBUG=True ./env/bin/python manage.py test
```

If MySQL test database creation fails due to permissions, use the database guidance in `.sdd/knowledge/django-sqlite-to-mysql-mariadb.md`.

## 2. Files Added Or Reworked

- `aficionados_network/test.py`
- `profiles/tests/tests_models.py`
- `profiles/tests/tests_views.py`
- `posts/tests.py`
- `notifications/tests.py`

One production fix was made while adding tests:

- `aficionados_network/views.py`
  - `ContactFormView` now renders `general/emails/notification_email.html`.
  - The previous path, `emails/notification_email.html`, did not match the actual template tree.

## 3. Coverage By Area

### Core App

File: `aficionados_network/test.py`

Coverage:

- Home page renders for anonymous users.
- Login and logout flow.
- Registration creates an inactive user.
- Registration sends activation email through in-memory email backend.
- Activation token enables the user.
- Activation sends welcome email.
- Contact form persists `ContactMessage`.
- Contact form sends branded email to `CONTACT_EMAIL`.
- `ContactMessage.__str__`.

### Profiles Models

File: `profiles/tests/tests_models.py`

Coverage:

- `UserProfile` is created automatically by signal for regular users.
- Superusers do not get automatic profiles from the signal.
- Birth date cannot be in the future.
- `age` property.
- `Hobby` slug generation and string representation.
- `UserHobby` uniqueness per `(profile, hobby)`.
- Follow/unfollow through `toggle_follow()`.
- Follow counts and relationship helpers.
- Self-follow validation.
- `Review` uniqueness per `(event, author)`.

### Profiles Routes

File: `profiles/tests/tests_views.py`

Coverage:

- Profile list excludes the current user.
- Profile list count context: all, following, not following.
- Profile detail POST toggles follow/unfollow.
- Follow creates a notification.
- Profile edit updates both `User` and `UserProfile`.
- Add/delete hobby for current profile.
- Add review for event organizer.
- Review creation creates a notification.

### Posts And Events

File: `posts/tests.py`

Coverage:

- Post image upload helper behavior.
- Image size validator rejects files over 5 MB.
- Post like/comment counts.
- Post absolute URL.
- Post deletion removes image file from disk.
- Comment validation rejects parent comments from another post.
- Event `is_past`, absolute URL, string representation.
- `EventComment` string representation.
- Like toggle creates/deletes notifications and returns JSON.
- Post comment creates a comment, notification, and email.
- Post modal detail returns partial template.
- Event list/detail expose level match context.
- Event create assigns organizer and adds organizer as participant.
- Attendance toggle adds/removes participant and sends emails.
- Organizer cancel creates event notification and email.
- Organizer reactivate clears cancellation state.
- Organizer event comment notifies participants.
- Event duplicate redirects to edit form.
- Hobby hub renders.
- Hobby membership toggle redirects correctly.
- Clicks gallery renders and includes context.

### Notifications

File: `notifications/tests.py`

Coverage:

- Notification default unread state.
- Notification string representation.
- Follow signal creates notification.
- Notification list filters current user and marks unread notifications as read.
- Unread-count endpoint returns count or empty response.
- Context processor returns unread count.
- Notification redirects mark items read.
- Redirect targets cover post, event, and follow/profile paths.

## 4. Test Design Conventions

Use these patterns for future tests:

- Prefer `TestCase` for database-backed Django behavior.
- Use `force_login()` for authenticated routes unless explicitly testing login.
- Use `reverse()` for URLs instead of hard-coded paths.
- Use `override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)` for route tests to avoid `.env` or production-security redirects.
- Use `EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"` and inspect `mail.outbox`.
- Use temporary `MEDIA_ROOT` for upload tests.
- Assert behavior, not implementation details: rows created, redirects, templates, context, notifications, email count/subject/recipient.
- Keep route tests close to user workflows: create/update/delete profile data, join/leave event, comment, notify, email.

## 5. Known Gaps And Next Useful Tests

The current suite removes the biggest manual-testing burden, but future work can add:

- Permission tests for unauthorized edit/delete/cancel actions.
- Event full-capacity rejection.
- Past-event attendance rejection.
- Search/filter combinations for event list and profile list.
- HTMX-specific responses for comments, clicks gallery, and hobby membership partials.
- Password reset email flow.
- Admin smoke tests for important model registrations.
- MySQL-specific test run in an environment with test database privileges.

## 6. Operational Note

If a future developer sees 301 failures in tests, first check whether `.env` selected production-like security settings. The baseline command above explicitly sets `DEBUG=True` and SQLite to avoid that drift.
