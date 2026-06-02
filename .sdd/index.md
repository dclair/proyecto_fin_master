# SDD Index

**Last reviewed:** 2026-06-01  
**Purpose:** single entry hub for Hubs&Clicks structured knowledge.

Start here whenever you open the project without fresh context.

## Read Order

1. `current-state.md`
   - What is true right now.
   - Runtime, verification, caveats, and operational commands.

2. `architecture-map.md`
   - Apps, models, routes, templates, assets, and cross-cutting flows.

3. `decision-log.md`
   - Important technical decisions and why they exist.

4. `changelog-logical.md`
   - Semantic history of the system.

5. Domain-specific knowledge under `knowledge/`
   - Deep dives and reusable patterns.

## Quick Commands

Run tests:

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py test --verbosity 1
```

Run local server with SQLite:

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py runserver
```

Run checks with SQLite:

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py check
```

## Knowledge Documents

Operational layer:

- `current-state.md`: single operational truth.
- `decision-log.md`: decisions and rationale.
- `architecture-map.md`: module and relationship map.
- `changelog-logical.md`: semantic system history.
- `index.md`: this hub.

Detailed knowledge:

- `knowledge/project-architecture-hubs-clicks.md`: full product and architecture baseline.
- `knowledge/testing-strategy-hubs-clicks.md`: 35-test baseline, command, coverage, conventions, gaps.
- `knowledge/django-sqlite-to-mysql-mariadb.md`: reusable DB migration guide.

Change records:

- `changes/sqlite-to-mysql-migration/ai-handoff.md`
- `changes/sqlite-to-mysql-migration/implementation-log.md`
- `changes/sqlite-to-mysql-migration/verification-report.md`
- `changes/sqlite-to-mysql-migration/tasks.md`
- `changes/sqlite-to-mysql-migration/spec.md`
- `changes/sqlite-to-mysql-migration/design.md`
- `changes/sqlite-to-mysql-migration/proposal.md`

## If You Are Going To Touch...

Profiles:

- Read `current-state.md`.
- Read `architecture-map.md` sections for `profiles`.
- Read tests in `profiles/tests/`.
- Watch for route duplication and follow notification behavior.

Posts/Clicks:

- Read `architecture-map.md` sections for `posts.Posts` and comments.
- Read `posts/tests.py`.
- Preserve image validation/cleanup, likes, comments, notifications, and email behavior.

Events/Quedadas:

- Read event lifecycle in `current-state.md` and `architecture-map.md`.
- Read `posts/tests.py`.
- Preserve organizer permissions, attendance constraints, cancellation/reactivation, notification/email behavior, and match/mentor context.

Notifications:

- Read `architecture-map.md` notification flow.
- Read `notifications/tests.py`.
- Preserve read marking, unread count, redirect targets, and fixture-safe signals.

Emails:

- Read `decision-log.md` D-006 and D-010.
- Use locmem backend in tests.
- Preserve branded HTML templates and CID logo behavior.

Database:

- Read `knowledge/django-sqlite-to-mysql-mariadb.md`.
- Preserve environment override behavior.
- Be careful with signals during fixture loads.

Testing:

- Read `knowledge/testing-strategy-hubs-clicks.md`.
- Run the SQLite test command before finalizing.
- Add tests close to changed behavior.

## Maintenance Rules

- Update `current-state.md` whenever operational truth changes.
- Update `decision-log.md` when making a meaningful technical choice.
- Update `architecture-map.md` when modules, routes, relationships, or flows change.
- Update `changelog-logical.md` for semantic changes.
- Keep detailed, reusable guides in `knowledge/`.
- Keep bounded change work in `changes/<change-name>/`.

## Current Caveats Snapshot

- MySQL may be selected by `.env`; tests should explicitly select SQLite.
- Media files are separate from DB state.
- Notifications and emails are both product contracts for many interactions.
