# Tasks: SQLite → MySQL/MariaDB Migration

**Status:** Automated migration complete; browser validation pending  
**Last updated:** 2026-05-25

## Completed

- [x] Reviewed proposal, specification, and design documents.
- [x] Confirmed SQLite backup exists: `db.sqlite3.backup`.
- [x] Added MySQL/MariaDB environment selection in Django settings.
- [x] Added strict MySQL SQL mode and persistent connection age.
- [x] Added PyMySQL fallback compatible with Django 6 backend loading.
- [x] Installed `PyMySQL==1.1.0` in the project virtual environment.
- [x] Added `.env.example` with SQLite and MySQL/MariaDB variables.
- [x] Added `.gitignore` entries for local secrets and generated migration dump.
- [x] Updated README with MySQL/MariaDB setup and SQLite dump/load commands.
- [x] Generated `db_full_backup.json` from SQLite using Django `dumpdata`.
- [x] Verified JSON fixture loads as valid JSON.
- [x] Fixed follow notification signal for current `Follow` model fields.
- [x] Fixed profile count methods and compatibility with tests/templates.
- [x] Added top-level profile URL aliases expected by the test suite.
- [x] Ran Django checks successfully against SQLite.
- [x] Ran Django test suite successfully against SQLite: 13 tests OK.
- [x] Verified Django can load MySQL backend configuration.
- [x] Verified local MySQL/MariaDB server responds, but requires credentials.
- [x] Created MySQL/MariaDB database `aficionados_network_db` with `utf8mb4`.
- [x] Created/granted `django_user` using the password configured in `.env`.
- [x] Ran `python manage.py migrate` against MySQL/MariaDB.
- [x] Prepared `django_site` record required by flatpages fixture data.
- [x] Ran `python manage.py loaddata db_full_backup.json`.
- [x] Compared SQLite fixture counts with MySQL table counts: all 16 model counts match.
- [x] Verified database and core tables use `utf8mb4_unicode_ci`.
- [x] Ran Django test suite against MySQL/MariaDB: 13 tests OK.
- [x] Confirmed `DB_ENGINE=sqlite` can still override `.env` for rollback/maintenance.
- [x] Verified no orphaned records in key relationships.
- [x] Verified sampled media file references exist on disk.
- [x] Verified User → UserProfile creation signal works on MySQL/MariaDB.

## Pending

- [ ] Browser-validate registration, posts, events, notifications, and media paths.

## Notes

The automated migration path is complete. The remaining item is browser validation of the user-facing workflows.
