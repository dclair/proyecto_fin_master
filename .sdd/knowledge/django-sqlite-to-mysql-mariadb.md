# Knowledge Base: Django SQLite to MySQL/MariaDB Migration

This document is a reusable guide for future Django projects and future AI agents. It captures the safe path, failure modes, and validation steps from a completed SQLite to MySQL/MariaDB migration.

## When To Use This Guide

Use this guide when a Django project:

- Currently uses SQLite.
- Needs MySQL or MariaDB for production-like concurrency and deployment.
- Uses Django ORM migrations.
- Has existing data that must be preserved.
- May include signals, flatpages, uploaded media, or many-to-many relationships.

## Recommended Strategy

Use Django's native dump/restore path:

1. Backup SQLite.
2. Add environment-based database settings.
3. Create MySQL/MariaDB database and app user.
4. Run Django migrations on MySQL/MariaDB.
5. Export SQLite data with `dumpdata`.
6. Prepare framework rows needed by natural keys, especially `django_site`.
7. Import data with `loaddata`.
8. Compare counts.
9. Run checks, tests, and integrity queries.
10. Browser-validate critical workflows.

Avoid direct SQLite-to-MySQL SQL conversion unless the project has a clear reason. Django fixtures preserve ORM-level relationships more reliably for ordinary Django apps.

## Settings Pattern

Use `.env` with shell override support:

```python
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")
```

Do not pass `override=True` if you want commands like this to work:

```bash
DB_ENGINE=sqlite python manage.py check
```

Use a simple selector:

```python
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").strip().lower()

if DB_ENGINE in {"mysql", "mariadb"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", ""),
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "600")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("SQLITE_NAME", "db.sqlite3"),
        }
    }
```

## Driver Choice

Prefer `mysqlclient` when system dependencies are available. Use `PyMySQL` when portability matters or C headers are unavailable.

For PyMySQL fallback in Django 6, configure it before Django loads the database backend:

```python
from importlib.util import find_spec

if find_spec("MySQLdb") is None and find_spec("pymysql") is not None:
    import pymysql

    pymysql.version_info = (2, 2, 1, "final", 0)
    pymysql.__version__ = "2.2.1"
    pymysql.install_as_MySQLdb()
```

## Database Setup

Use `utf8mb4` everywhere:

```sql
CREATE DATABASE app_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'django_user'@'127.0.0.1' IDENTIFIED BY '<strong-password>';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX
  ON app_db.*
  TO 'django_user'@'127.0.0.1';

FLUSH PRIVILEGES;
```

For tests, the app user also needs permission to create and destroy the test database:

```sql
GRANT ALL PRIVILEGES ON test_app_db.* TO 'django_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

## Dump And Load

Backup:

```bash
cp db.sqlite3 db.sqlite3.backup
```

Dump:

```bash
DB_ENGINE=sqlite python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --indent 2 \
  -e sessions \
  -e sites \
  > db_full_backup.json
```

Migrate schema:

```bash
DB_ENGINE=mysql python manage.py migrate --no-input
```

Load:

```bash
DB_ENGINE=mysql python manage.py flush --noinput
DB_ENGINE=mysql python manage.py loaddata db_full_backup.json
```

## Signal Safety

Every signal that creates related records should protect fixture loading:

```python
@receiver(post_save, sender=SomeModel)
def handler(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return
    if created:
        ...
```

Why: during `loaddata`, the database may not yet contain related rows that the signal expects.

## Flatpages And Sites

If the project uses `django.contrib.flatpages`, flatpages reference sites through a many-to-many relation. If `sites` is excluded from the fixture, create the matching site rows before loading flatpages.

Example:

```sql
INSERT INTO django_site (id, domain, name)
VALUES (1, '127.0.0.1:8000', '127.0.0.1:8000')
ON DUPLICATE KEY UPDATE domain=VALUES(domain), name=VALUES(name);
```

Alternative: include `sites` in the fixture and handle any environment-specific site changes after load.

## Count Verification Pattern

Compare fixture counts to ORM counts:

```python
import json
from collections import Counter
from django.apps import apps

data = json.load(open("db_full_backup.json"))
counts = Counter(row["model"] for row in data)

for label, expected in sorted(counts.items()):
    model = apps.get_model(label)
    actual = model._default_manager.count()
    print(label, expected, actual, expected == actual)
```

## Integrity Checks

Run project-specific orphan checks. Examples:

```sql
SELECT COUNT(*)
FROM posts_comment c
LEFT JOIN posts_posts p ON c.post_id = p.id
WHERE p.id IS NULL;

SELECT COUNT(*)
FROM notifications_notification n
LEFT JOIN auth_user u ON n.recipient_id = u.id
WHERE u.id IS NULL;
```

Also verify:

- Many-to-many table counts.
- Unique constraints.
- Signals on new records.
- Media files exist for image/file fields.

## Media Files

Database migration only moves file paths. It does not move files.

Always verify:

- `MEDIA_ROOT` is unchanged or files were copied.
- Referenced files exist.
- Web server can serve media in the target environment.

## Rollback

Keep SQLite backup until the MySQL/MariaDB app has been manually validated.

Rollback command pattern:

```bash
DB_ENGINE=sqlite python manage.py runserver
```

If `.env` defaults to MySQL/MariaDB, a shell override is enough as long as `load_dotenv` does not override shell variables.

## Final Checklist

- [ ] SQLite backup exists.
- [ ] MySQL/MariaDB database exists with `utf8mb4`.
- [ ] App user has scoped privileges.
- [ ] Django migrations applied.
- [ ] Fixture loads without errors.
- [ ] Counts match.
- [ ] Tests pass.
- [ ] No orphaned rows in critical relationships.
- [ ] Media references resolve.
- [ ] Signals work on new records.
- [ ] Browser workflows pass.

