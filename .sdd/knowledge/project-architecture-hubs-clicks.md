# Knowledge Base: Hubs&Clicks Project Architecture

**Last reviewed:** 2026-06-01  
**Project type:** Django social web application  
**Main product:** Hubs&Clicks, a social network for connecting users through hobbies, posts, events, participation, follows, comments, likes, reviews, notifications, and branded emails.

This document is the baseline project map for future developers and AI agents. It intentionally complements the existing `.sdd` MySQL migration documents; database migration details live in `.sdd/knowledge/django-sqlite-to-mysql-mariadb.md` and `.sdd/changes/sqlite-to-mysql-migration/`.

## 1. Product Summary

Hubs&Clicks lets users:

- Register with email activation and later log in/log out.
- Maintain a social profile with photo, bio, location, website, age, hobbies, and experience levels.
- Follow/unfollow other profiles.
- Publish image-based posts called Clicks, assign them to a hobby, like them, and comment on them.
- Create and manage hobby-based events called Quedadas.
- Join or leave events when allowed by date, ownership, and capacity rules.
- Cancel, reactivate, duplicate, edit, and list their own events.
- See personal participation history and review event organizers after attended events.
- Receive in-app notifications for follows, likes, comments, event changes, and reviews.
- Receive branded HTML emails for important interactions.
- Send contact messages to the site owner/admin.

The application is mostly server-rendered Django templates with Bootstrap, vanilla JavaScript, AJAX, and some HTMX-oriented partial responses.

## 2. Runtime Stack

- Python: intended for Python 3.12.
- Django: `Django==6.0`.
- Database: selected by environment.
  - SQLite for local fallback: `DB_ENGINE=sqlite`.
  - MySQL/MariaDB for current migrated local state: `DB_ENGINE=mysql` or `mariadb`.
- MySQL driver: `PyMySQL==1.1.0`, installed as `MySQLdb` fallback in settings.
- Static serving: Django staticfiles, optional WhiteNoise if installed.
- Forms/UI: `django-crispy-forms`, `crispy-bootstrap5`, Bootstrap templates.
- Images: Pillow for upload validation/processing.
- Email: Django `EmailMultiAlternatives`, HTML templates, CID-attached logos.

Key dependency file: `requirements.txt`.

## 3. High-Level Directory Map

- `manage.py`: Django command entrypoint.
- `aficionados_network/`: project package and also a local Django app for general views and contact messages.
- `posts/`: posts, comments, events, event comments, event participation, hub pages, clicks gallery, and event email flows.
- `profiles/`: user profiles, hobbies, hobby levels, follows, reviews, profile views, and profile editing.
- `notifications/`: notification model, notification list, unread counter endpoint, redirect logic, and follow signal.
- `aficionados_network/templates/`: main template tree used by all apps.
- `profiles/templates/`: profile-specific templates also present under the app.
- `static/`: global CSS, JavaScript, logos, default images.
- `media/`: uploaded user/media files; database stores paths only.
- `.sdd/`: structured design/delivery documentation and reusable knowledge.

Generated/local operational files that should not be treated as source-of-truth code:

- `db.sqlite3`
- `db.sqlite3.backup`
- `db_full_backup.json`
- `.env`
- `env/`
- `__pycache__/`

## 4. Django Settings And Boot

Main settings: `aficionados_network/settings.py`.

Important settings behavior:

- Loads `.env` with `load_dotenv(os.path.join(BASE_DIR, ".env"))`.
- Shell environment variables can override `.env` values.
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS` are environment-driven.
- Production guards raise `ValueError` if `DEBUG=False` with insecure secret or missing hosts.
- `SITE_ID` defaults to `1`, required by `django.contrib.sites` and flatpages.
- `FlatpageFallbackMiddleware` is enabled.
- Template context processors include:
  - `notifications.context_processors.unread_notifications`
  - `profiles.context_processors.user_hobbies_processor`
- `MEDIA_ROOT = BASE_DIR / "media"` and `MEDIA_URL = "/media/"`.
- `STATICFILES_DIRS` points at the top-level `static/`.
- Email defaults currently target SMTP/Gmail-style configuration unless overridden.

Database selection:

- `DB_ENGINE in {"mysql", "mariadb"}` uses `django.db.backends.mysql`, `utf8mb4`, strict transactions, and configurable `CONN_MAX_AGE`.
- Any other `DB_ENGINE` uses SQLite with `SQLITE_NAME` defaulting to `db.sqlite3`.

## 5. Installed Apps

Core Django apps:

- `django.contrib.admin`
- `django.contrib.auth`
- `django.contrib.contenttypes`
- `django.contrib.sessions`
- `django.contrib.messages`
- `django.contrib.staticfiles`
- `django.contrib.sites`
- `django.contrib.flatpages`

Third-party apps:

- `django_extensions`
- `crispy_forms`
- `crispy_bootstrap5`

Project apps:

- `posts`
- `profiles`
- `aficionados_network`
- `notifications`

Important note: `ProfilesConfig.ready()` imports `profiles.signals`; `NotificationsConfig.ready()` imports `notifications.signals`. Signal behavior matters during fixture loading and migrations.

## 6. Domain Model Map

### `profiles.Hobby`

Represents an interest/affinity category such as photography, cycling, etc.

Fields:

- `name`: unique human-readable name.
- `description`: optional text.
- `slug`: unique slug, generated from `name` on save when missing.

Relations:

- Used by `profiles.UserHobby` to connect users with interests and levels.
- Used by `posts.Posts.category`.
- Used by `posts.Event.hobby`.

### `profiles.UserProfile`

One-to-one extension of Django `User`.

Fields:

- `user`
- `profile_picture`
- `bio`
- `birth_date`
- `location`
- `website`
- `created_at`
- `updated_at`

Relations:

- `followers`: self many-to-many through `Follow`, asymmetric.
- `hobbies`: many-to-many to `Hobby` through `UserHobby`.

Useful methods/properties:

- `profile_picture_url`
- `followers_count()`
- `following_count()`
- `age`
- `is_following(profile)`
- `is_followed_by(profile)`
- `toggle_follow(profile)`

Important behavior:

- `profiles.signals.create_user_profile` creates a profile automatically for new non-superuser `User` rows.
- Self-follow is blocked by model validation and an `m2m_changed` signal.

### `profiles.UserHobby`

Intermediate model for a user's hobby and experience level.

Fields:

- `profile`
- `hobby`
- `level`: `beginner`, `intermediate`, `advanced`, `expert`

Constraint:

- Unique pair: `(profile, hobby)`.

This model powers event matching and mentor tags in home, event list/detail, and hobby hub views.

### `profiles.Follow`

Directed follow relationship between two `UserProfile` rows.

Fields:

- `follower`
- `following`
- `created_at`

Constraint:

- Unique pair: `(follower, following)`.

Important behavior:

- Cannot follow self.
- Creating a follow triggers `notifications.signals.create_follow_notification`.

### `profiles.Review`

Post-event rating from a participant to an event organizer.

Fields:

- `event`: FK to `posts.Event`.
- `author`: user writing the review.
- `recipient`: organizer receiving the review.
- `rating`: 1-5.
- `comment`
- `created_at`

Constraint:

- Unique pair: `(event, author)`.

Important behavior:

- Review creation in `profiles.views.add_review` also creates a `review` notification.

### `posts.Posts`

Image-oriented social post, called a Click in the product.

Fields:

- `user`: author.
- `title`
- `image`
- `caption`
- `location`
- `created_at`
- `updated_at`
- `likes`: many-to-many to `User`.
- `slug`
- `category`: FK to `profiles.Hobby`.

Important behavior:

- Image file extension and size validation.
- Save attempts to resize images larger than 1080x1080.
- Delete removes the image file from disk.
- `total_likes`, `total_comments`, `user_has_liked(user)`, `get_absolute_url()`.

Notes:

- The `slug` field is present but current detail route uses primary key.
- The custom `save()` contains a leftover self-follow check referencing `following`; it does not appear relevant to posts.

### `posts.Comment`

Comment or reply on a `Posts` row.

Fields:

- `user`
- `post`
- `comment`
- `created_at`
- `updated_at`
- `parent`: optional self FK for replies.

Validation:

- A comment cannot be its own parent.
- Parent comment must belong to the same post.

### `posts.Event`

Hobby-based event/quedada.

Fields:

- `title`
- `description`
- `location`
- `event_date`
- `image`
- `created_at`
- `is_canceled`
- `organizer`
- `hobby`
- `participants`: many-to-many to `User`.
- `max_participants`
- `level`: `all`, `beginner`, `intermediate`, `advanced`, `expert`.

Important behavior:

- `is_past` compares `event_date` with `timezone.now()`.
- `get_absolute_url()` points to `posts:event_detail`.
- Ordered by upcoming date.

### `posts.EventComment`

Linear comment thread on an event.

Fields:

- `event`
- `user`
- `content`
- `created_at`

### `notifications.Notification`

In-app notification.

Fields:

- `recipient`
- `sender`
- `notification_type`: `follow`, `like`, `comment`, `event`, `review`.
- Optional links: `post`, `event`, `review`, `comment`.
- `is_read`
- `created_at`

Important behavior:

- Ordered newest first.
- List view marks notifications read when opened.
- Redirect endpoints mark individual notifications read and route users to the relevant post, event, profile, or notification list fallback.

### `aficionados_network.ContactMessage`

Stored contact form submission.

Fields:

- `name`
- `email`
- `subject`
- `message`
- `created_at`
- `read`

Admin can filter/search these messages.

## 7. URL Map

Root URL config: `aficionados_network/urls.py`.

Top-level routes:

- `/admin/`: Django admin.
- `/`: `HomeView`.
- `/events/`: includes `posts.urls`.
- `/profile/`: includes `profiles.urls`.
- `/profile/list/`: profile list shortcut using `profiles.views.ProfilesListView`.
- `/profile/<int:pk>/`: profile detail shortcut using `profiles.views.ProfileView`.
- `/login/`, `/logout/`, `/register/`: auth views in `aficionados_network.views`.
- `/activate/<uidb64>/<token>/`: registration activation.
- `/password-reset/...`: Django password reset views with custom templates.
- `/contact/`: contact form.
- `/legal/`, `/privacidad/`, `/politica-cookies/`, `/cookies/`: static legal pages.
- `/pages/`: flatpages.
- `/notifications/`: includes `notifications.urls`.

`posts.urls`, mounted under `/events/`:

- `/events/`: upcoming event list.
- `/events/new/`: create event.
- `/events/<event_id>/toggle/`: join/leave event.
- `/events/<pk>/`: event detail.
- `/events/<pk>/edit/`: edit event.
- `/events/<pk>/cancel/`: cancel event.
- `/events/<event_id>/comment/`: add event comment.
- `/events/event/<pk>/reactivate/`: reactivate canceled event.
- `/events/event/<pk>/duplicate/`: duplicate event.
- `/events/hub/<hobby_slug>/`: hobby hub.
- `/events/mis-inscripciones/`: events where current user participates.
- `/events/mis-planes-organizados/`: events organized by current user.
- `/events/clicks/`: mixed gallery of post/event images.
- `/events/hobby/toggle/<hobby_slug>/`: join/leave hobby membership.
- `/events/create/`: create post/click.
- `/events/post/<pk>/`: post detail.
- `/events/like/<post_id>/`: AJAX like toggle.
- `/events/post/<post_id>/comment/`: add post comment.
- `/events/post/<pk>/edit/`: edit post.
- `/events/post/<pk>/delete/`: delete post.

`profiles.urls`, mounted under `/profile/`:

- `/profile/profile/list/`: profile list inside namespace.
- `/profile/profile/<pk>/`: profile detail inside namespace.
- `/profile/profile/edit/`: edit own profile.
- `/profile/hobby/add/`: add hobby to own profile.
- `/profile/hobby/delete/<hobby_id>/`: remove hobby from own profile.
- `/profile/review/add/<event_id>/`: add review.

Important route caveat:

- There are duplicated profile-list/detail routes: top-level `/profile/list/` and `/profile/<pk>/`, plus namespaced routes under `/profile/profile/...`. Existing templates/tests may use both global names (`profile`, `profile_list`) and namespaced names (`profiles:profile`, `profiles:profile_edit`). Be careful when changing route names.

`notifications.urls`, mounted under `/notifications/`:

- `/notifications/`: list and mark all read.
- `/notifications/read/<pk>/`: read and redirect.
- `/notifications/api/unread-count/`: unread count response for async polling/HTMX.
- `/notifications/go/<notification_id>/`: read and redirect alternate endpoint.

## 8. Main View Flows

### Home Feed

View: `aficionados_network.views.HomeView`.

Behavior:

- Authenticated users with profiles see posts from followed profiles first.
- If no followed posts exist, the home falls back to recent global posts.
- Anonymous users see recent global posts.
- Upcoming events are filtered by the authenticated user's hobbies when available.
- Each hobby in the sidebar receives a computed `match_count`.
- Upcoming events get runtime attributes such as `is_match` and `is_mentor`.

### Registration And Activation

Views: `RegisterView`, `activate`.

Behavior:

- Registration creates inactive user.
- Sends activation email using `registration/acc_active_email.html`.
- Activation token enables `is_active`.
- Successful activation sends a welcome email using `registration/welcome_email.html`.
- Logos are attached by CID from `static/img/logo_hubs.png`.

### Profile Detail/Edit

Primary current views are in `profiles/views.py`.

Profile detail:

- Shows organized and participated event counts.
- Shows next three non-canceled activities.
- Shows followers/following and whether current user follows target profile.
- Shows received reviews, count, and average rating.
- POST toggles follow/unfollow and may create follow notification.

Profile edit:

- Updates Django `User` fields and `UserProfile` fields.
- Shows existing `UserHobby` rows and all hobbies.
- Separate add/delete views manage hobby levels.

### Post/Click Creation And Interaction

Views: `posts.views.PostCreateView`, `PostDetailView`, `toggle_like`, `add_comment`.

Behavior:

- Post creation assigns `request.user` as author.
- Post creation context also builds a global discovery feed, stats, and trending categories.
- Detail can return a modal partial when `?modal=...` is passed.
- Likes are toggled by POST and return JSON `{liked, count}`.
- Like notification is created only when liking another user's post.
- Comment creation notifies post owner, or notifies prior participants when the author replies in their own post thread.
- HTMX comment requests return `posts/partials/_comment_single.html`.

### Event Lifecycle

Views: `EventListView`, `EventCreateView`, `EventDetailView`, `EventUpdateView`, `EventCancelView`, `EventReactivateView`, `duplicate_event`, `toggle_attendance`, `add_event_comment`.

Behavior:

- Event list only shows future events and supports filters: search `q`, `city`, `hobby`, `level`.
- User hobby levels are used to set `event.is_match`.
- Event create assigns organizer and automatically adds the organizer as participant.
- Detail shows participants, comment form, level match, and mentor status.
- Organizer-only edit/cancel/reactivate actions use `UserPassesTestMixin`.
- Join/leave is blocked when event is past.
- Organizer cannot leave their own event.
- Capacity is enforced before adding participants.
- Canceling an event sets `is_canceled=True`, creates event notifications for participants, and sends emails.
- Reactivating a future canceled event reverses the canceled flag and notifies participants.
- Duplicating an event creates a copy for the same organizer and redirects to edit.
- Event comments notify either the organizer or all participants when the organizer replies.

### Participation And Reviews

Views: `MyParticipationsListView`, `profiles.views.add_review`.

Behavior:

- Participation list shows all events where current user is a participant.
- Each row is annotated with `has_reviewed`.
- Review creation prevents duplicate review by `(event, author)`.
- Review recipient is always `event.organizer`.
- Creates a `review` notification.

### Clicks Gallery And Hobby Hub

Views: `clicks_gallery`, `hobby_hub`, `toggle_hobby_membership`.

Behavior:

- Clicks gallery merges image posts and image events, sorts by `created_at`, paginates 12 per page, and returns a partial for HTMX requests.
- Hobby hub shows events and recent posts for one hobby.
- Hobby hub computes member count and user match/mentor tags.
- Hobby membership toggle uses `profile.hobbies.add/remove(hobby)`; because the M2M uses through `UserHobby`, this may rely on Django creating a through row with default level. Test carefully if changing `UserHobby` required fields.

### Notifications

Views: `NotificationListView`, `notification_redirect`, `api_unread_count`, `read_and_redirect`.

Behavior:

- Context processor exposes `unread_notifications_count` globally.
- Notification list filters to current user and marks all unread items as read.
- API unread count returns an empty string for zero.
- Redirect logic sends users to the linked event, post, profile, or fallback list.

## 9. Templates And Static Assets

Main layout and shared includes:

- `aficionados_network/templates/general/layout.html`
- `aficionados_network/templates/_includes/_header.html`
- `aficionados_network/templates/_includes/_footer.html`
- `aficionados_network/templates/_includes/_messages.html`
- `aficionados_network/templates/_includes/_post.html`
- `aficionados_network/templates/_includes/_event_card.html`
- `aficionados_network/templates/_includes/_cookies_banner.html`

General pages:

- `general/home.html`
- `general/login.html`
- `general/logout.html`
- `general/register.html`
- `general/contact.html`
- `general/legal.html`
- `general/privacy.html`
- `general/cookies_policy.html`
- `general/password_reset/*`

Registration/email templates:

- `registration/acc_active_email.html`
- `registration/welcome_email.html`
- `registration/confirm_email_sent.html`
- `registration/activation_success.html`
- `registration/activation_invalid.html`
- `general/emails/notification_email.html`

Posts/events templates:

- `posts/event_list.html`
- `posts/event_detail.html`
- `posts/event_form.html`
- `posts/event_confirm_delete.html`
- `posts/my_events.html`
- `posts/my_participations.html`
- `posts/hobby_hub.html`
- `posts/clicks_list.html`
- `posts/post_create.html`
- `posts/post_detail.html`
- `posts/post_update.html`
- `posts/post_confirm_delete.html`
- `posts/partials/*`

Profiles templates:

- `profiles/templates/profiles/profile.html`
- `profiles/templates/profiles/profile_list.html`
- `profiles/templates/profiles/profile_detail.html`
- `profiles/templates/profiles/profile_edit.html`

Notification templates:

- `aficionados_network/templates/notifications/list.html`

Static JavaScript:

- `static/js/forms.js`: form/image behavior.
- `static/js/community-hub.js`: community/hub interactions.
- `static/js/cookies.js`: cookie banner.
- `static/js/ajax-hubs.js`: asynchronous hub behavior.
- `static/js/likes.js`: AJAX like behavior.
- `static/js/comentarios.js`: comments behavior.

Static images:

- `static/img/logo_hubs.png`
- `static/img/logo_hubs_email.png`
- `static/img/hubs&clicks.png`
- `static/img/default_profile.png`
- `static/img/default_event.png`

## 10. Signals And Side Effects

Registered signals:

- `profiles.signals.create_user_profile`
  - Sender: `User`.
  - Creates `UserProfile` for new non-superuser users.
  - Uses `transaction.atomic()` and logs errors.

- `profiles.signals.prevent_self_follow`
  - Sender: `UserProfile.following.through`.
  - Blocks adding current profile to its own following set.

- `notifications.signals.create_follow_notification`
  - Sender: `Follow`.
  - Creates notification when a follow row is created.
  - Explicitly returns during fixture load when `kwargs.get("raw")` is true.

Important fixture-loading lesson:

- Any future signal that creates related records must check `kwargs.get("raw")` before doing work. This was a key lesson from the SQLite to MySQL migration.

## 11. Admin Surface

Admin registrations:

- `posts`: `Posts`, `Comment`, `Event`.
- `profiles`: `UserProfile`, `Follow`, `Hobby`, `UserHobby`, `Review`.
- `notifications`: `Notification`.
- `aficionados_network`: `ContactMessage`.

Admin classes include useful list displays, filters, search fields, and profile image preview for `UserProfile`.

## 12. Testing And Verification

Current test files:

- `profiles/tests/tests_models.py`
- `profiles/tests/tests_views.py`
- `posts/tests.py`
- `notifications/tests.py`
- `aficionados_network/test.py`

As of 2026-06-01, the suite has 35 tests covering:

- Core views and emails: home, login/logout, registration, activation, contact form, `ContactMessage`.
- Profile models: automatic profile signal, superuser profile exception, age/birth-date validation, hobbies, user hobby uniqueness, follows, review uniqueness.
- Profile routes: profile list/detail, follow/unfollow notifications, profile edit, add/delete hobbies, add review.
- Post models/routes: image validation, post image delete cleanup, likes, comments, modal partial, notification/email creation.
- Event models/routes: event helpers, event comments, list/detail matching context, create, attendance toggle, cancel, reactivate, duplicate, organizer comments, hobby hub, clicks gallery.
- Notifications: model string/default state, follow signal, list read marking, unread-count endpoint, context processor, smart redirects.

Primary development command:

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py test --verbosity 1
```

Why this command:

- The local `.env` may select MySQL/MariaDB by default.
- In the sandbox, MySQL socket access can fail with `PermissionError: [Errno 1] Operation not permitted`.
- SQLite keeps the test run fast and isolated for ordinary feature work.

Optional database-specific checks:

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py test
env DB_ENGINE=mysql DEBUG=True ./env/bin/python manage.py test
```

If MySQL permissions block test database creation, see `.sdd/knowledge/django-sqlite-to-mysql-mariadb.md`.

Testing conventions now in place:

- Use `override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)` in route tests to avoid environment-driven redirects.
- Use `EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"` and inspect `django.core.mail.outbox` for email assertions.
- Use a temporary `MEDIA_ROOT` for image upload tests so tests do not write into project `media/`.
- Prefer `force_login()` for authenticated route tests unless the login flow itself is under test.
- Keep tests focused on observable product behavior: database rows, redirects, templates, context, notifications, and emails.

Manual smoke-test workflows after meaningful changes:

1. Register a new user and activate by email link.
2. Log in, edit profile, add hobbies with levels.
3. Create a post with image, like/comment from another user.
4. Create an event, join with another user, comment as participant and organizer.
5. Cancel/reactivate event and verify in-app notifications and email behavior.
6. Visit home, event list filters, hobby hub, clicks gallery, notification list.
7. Mark notifications through redirect links and verify unread count.
8. Review an organizer after a past participation.

## 13. Known Caveats For Future Work

- There are duplicated/older profile classes in `aficionados_network/views.py` with templates under `general/profile*`. Current top-level URL config imports profile list/detail from `profiles.views`, while auth/home/contact still come from `aficionados_network.views`.
- `aficionados_network/views.py` defines `HomeView` twice; the second definition is the effective one.
- Profile routes exist both as global names and namespaced profile URLs. Check templates before renaming.
- `notifications/context_procesors.py` appears to be a misspelled duplicate-like file; settings use `notifications.context_processors`.
- `posts.Posts.save()` includes unrelated self-follow validation logic that likely came from older code.
- `ContactFormView` was corrected on 2026-06-01 to render `"general/emails/notification_email.html"` so contact emails use the existing template path.
- `EventComment` is not registered in `posts/admin.py` at the time of this review.
- Event-level match flags (`is_match`, `is_mentor`) are runtime attributes added in views, not model fields.
- The product uses both internal notifications and emails; preserve both surfaces when changing interaction flows.
- Uploaded media must be backed up/copied separately from database dumps.

## 14. Where To Add Future Documentation

- Use `.sdd/knowledge/` for reusable project-wide facts and patterns.
- Use `.sdd/changes/<change-name>/` for a bounded change with proposal/spec/design/tasks/verification/handoff documents.
- Keep database migration knowledge in the existing MySQL/MariaDB documents rather than duplicating it here.
