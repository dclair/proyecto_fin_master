# AI Handoff: SQLite to MySQL/MariaDB Migration

This file is written for a future AI or developer continuing the project without prior conversation context.

## Current Ground Truth

- The project is a Django 6.0 application.
- The migration from SQLite to MySQL/MariaDB has been executed successfully.
- `.env` selects MySQL/MariaDB by default with `DB_ENGINE=mysql`.
- `DB_ENGINE=sqlite` can be provided at command time to use `db.sqlite3`.
- The SQLite backup file is present as `db.sqlite3.backup`.
- The generated fixture is present as `db_full_backup.json`.
- The fixture and `.env` are local operational files and should not be committed.

## Do Not Lose These Lessons

1. Signals must handle fixture loads.
   - `loaddata` calls model saves with `raw=True`.
   - Any signal that touches related objects should return early when `kwargs.get("raw")` is true.

2. Flatpages and sites interact.
   - If `dumpdata` excludes `sites` but includes `flatpages`, create the matching `django_site` rows before `loaddata`.
   - This project needed `django_site(id=1, domain='127.0.0.1:8000')`.

3. Shell env vars should override `.env`.
   - This is important for rollback commands such as `DB_ENGINE=sqlite python manage.py check`.
   - Do not use `load_dotenv(..., override=True)` unless there is a deliberate reason.

4. PyMySQL works as a fallback, but Django 6 checks the MySQLdb version.
   - If `mysqlclient` is unavailable, install PyMySQL and configure it before Django loads the DB backend.
   - This project patches PyMySQL's exposed version for Django 6 compatibility.

5. Do not grant app users global database privileges.
   - Application DB user should get privileges scoped to the app database.
   - Test database privileges may be needed for `manage.py test`.

## Known Local State

- Database: `aficionados_network_db`
- App DB user: `django_user`
- Host: `127.0.0.1`
- Port: `3306`
- App DB password: stored in `.env`, not in documentation.

## Migration Recovery Commands

Use SQLite rollback/check:

```bash
DB_ENGINE=sqlite python manage.py check
DB_ENGINE=sqlite python manage.py runserver
```

Regenerate fixture from SQLite:

```bash
DB_ENGINE=sqlite python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --indent 2 \
  -e sessions \
  -e sites \
  > db_full_backup.json
```

Reload MySQL/MariaDB from fixture:

```bash
python manage.py flush --noinput
python manage.py loaddata db_full_backup.json
```

## What To Do Next

1. Run browser validation using `verification-report.md`.
2. If browser validation passes, mark `tasks.md` status as complete.
3. Consider archiving this change under whatever SDD archive convention the team adopts.
4. Before production deployment, replace local development secrets with managed production secrets.

