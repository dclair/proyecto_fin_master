# Implementation Log: SQLite to MySQL/MariaDB Migration

**Project:** Hubs&Clicks / Aficionados Network  
**Change:** `sqlite-to-mysql-migration`  
**Execution date:** 2026-05-25  
**Status:** Automated migration complete; browser workflow validation pending.

## Final State

- Django uses MySQL/MariaDB by default through `.env`.
- SQLite remains available for rollback or maintenance with `DB_ENGINE=sqlite`.
- Source SQLite database is retained as `db.sqlite3`.
- Safety backup is retained as `db.sqlite3.backup`.
- Data export fixture is retained locally as `db_full_backup.json` and ignored by Git.
- MySQL/MariaDB database name: `aficionados_network_db`.
- Application database user: `django_user`.
- Database charset/collation: `utf8mb4` / `utf8mb4_unicode_ci`.

## Files Changed

- `aficionados_network/settings.py`
  - Loads `.env` using `python-dotenv`.
  - Supports `DB_ENGINE=sqlite`, `DB_ENGINE=mysql`, and `DB_ENGINE=mariadb`.
  - Configures MySQL/MariaDB with `utf8mb4`.
  - Enables strict SQL mode with `STRICT_TRANS_TABLES`.
  - Adds `CONN_MAX_AGE` via `DB_CONN_MAX_AGE`.
  - Adds PyMySQL fallback for environments without `mysqlclient`.

- `requirements.txt`
  - Includes `PyMySQL==1.1.0`.

- `.env.example`
  - Documents all database variables required for SQLite and MySQL/MariaDB.

- `.gitignore`
  - Ignores local secrets, generated DB fixtures, venv, media, and collected static files.

- `README.md`
  - Documents MySQL/MariaDB setup, migration commands, and fixture import flow.

- `notifications/signals.py`
  - Uses current `Follow` model fields: `follower` and `following`.
  - Skips notification creation during fixture loads with `raw=True`.

- `profiles/models.py`
  - Keeps profile/follow helper methods aligned with existing tests.

- `aficionados_network/urls.py`
  - Adds top-level profile route aliases required by the current test suite.

## Commands Executed

Database and user setup:

```bash
mysql -u root -h 127.0.0.1 --execute "
CREATE DATABASE IF NOT EXISTS aficionados_network_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'django_user'@'127.0.0.1'
  IDENTIFIED BY '<app-db-password>';

ALTER USER 'django_user'@'127.0.0.1'
  IDENTIFIED BY '<app-db-password>';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX
  ON aficionados_network_db.*
  TO 'django_user'@'127.0.0.1';

FLUSH PRIVILEGES;
"
```

Schema migration:

```bash
python manage.py migrate --no-input
```

SQLite export:

```bash
DB_ENGINE=sqlite python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --indent 2 \
  -e sessions \
  -e sites \
  > db_full_backup.json
```

Fixture prerequisite for flatpages:

```sql
INSERT INTO django_site (id, domain, name)
VALUES (1, '127.0.0.1:8000', '127.0.0.1:8000')
ON DUPLICATE KEY UPDATE domain=VALUES(domain), name=VALUES(name);
```

Data import:

```bash
python manage.py flush --noinput
python manage.py loaddata db_full_backup.json --verbosity=2
```

## Verification Results

Fixture import:

```text
Installed 574 object(s) from 1 fixture(s)
```

Model count comparison:

```text
admin.logentry: 75 == 75
aficionados_network.contactmessage: 5 == 5
auth.permission: 76 == 76
auth.user: 6 == 6
contenttypes.contenttype: 19 == 19
flatpages.flatpage: 2 == 2
notifications.notification: 170 == 170
posts.comment: 100 == 100
posts.event: 24 == 24
posts.eventcomment: 44 == 44
posts.posts: 13 == 13
profiles.follow: 10 == 10
profiles.hobby: 4 == 4
profiles.review: 11 == 11
profiles.userhobby: 9 == 9
profiles.userprofile: 6 == 6
COUNTS_OK: True
```

Charset/collation:

```text
Database: utf8mb4 / utf8mb4_unicode_ci
posts_posts: utf8mb4_unicode_ci
notifications_notification: utf8mb4_unicode_ci
profiles_userprofile: utf8mb4_unicode_ci
```

Django checks and tests:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py test
Ran 13 tests in 11.640s
OK
```

Integrity checks:

```text
posts_comment_orphans: 0
events_organizer_orphans: 0
events_hobby_orphans: 0
notifications_recipient_orphans: 0
reviews_event_orphans: 0
missing_media: 0
profile_signal: True
```

## Issues Encountered And Fixes

### PyMySQL Version Detection With Django 6

Problem: Django 6 requires a MySQLdb-compatible driver reporting `mysqlclient >= 2.2.1`. PyMySQL installs a MySQLdb-compatible API but reports a legacy version.

Fix: When `MySQLdb` is unavailable and `pymysql` is present, configure PyMySQL as MySQLdb and patch the reported version before Django imports the MySQL backend.

### Environment Variable Precedence

Problem: For rollback and maintenance, commands like `DB_ENGINE=sqlite python manage.py ...` must override `.env`.

Fix: Use `load_dotenv(... )` without `override=True`, so shell-provided variables keep precedence over `.env`.

### Signals During Fixture Load

Problem: `loaddata` saves objects with `raw=True`; relationship-dependent signals can run before all fixture records exist.

Fix: Signal handlers that create derived records return immediately when `kwargs.get("raw")` is true.

### Flatpages Need A Matching Site

Problem: The fixture excluded `sites`, but `flatpages.flatpage.sites` referenced `127.0.0.1:8000`.

Fix: Insert or update `django_site(id=1, domain='127.0.0.1:8000')` before loading the fixture.

## Remaining Manual Validation

- Login and registration.
- Create/edit/delete a post.
- Create/join/cancel an event.
- Comments and likes.
- Notification bell and notification links.
- Media display for post images, event images, and profile pictures.

