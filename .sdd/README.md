# SDD Workspace

This directory stores structured design and delivery documentation for the project.

Start here:

1. `index.md`
2. `current-state.md`
3. `architecture-map.md`
4. `decision-log.md`
5. `changelog-logical.md`

## Active/Recent Changes

### `sqlite-to-mysql-migration`

Migration of the Django project from SQLite to MySQL/MariaDB.

Read in this order:

1. `changes/sqlite-to-mysql-migration/ai-handoff.md`
2. `changes/sqlite-to-mysql-migration/implementation-log.md`
3. `changes/sqlite-to-mysql-migration/verification-report.md`
4. `changes/sqlite-to-mysql-migration/tasks.md`
5. `changes/sqlite-to-mysql-migration/spec.md`
6. `changes/sqlite-to-mysql-migration/design.md`
7. `changes/sqlite-to-mysql-migration/proposal.md`

Reusable knowledge:

- `current-state.md`
- `architecture-map.md`
- `decision-log.md`
- `changelog-logical.md`
- `knowledge/project-architecture-hubs-clicks.md`
- `knowledge/testing-strategy-hubs-clicks.md`
- `knowledge/django-sqlite-to-mysql-mariadb.md`

## Notes For Future AI Agents

- Read `index.md` first. It is the hub for the entire `.sdd` workspace.
- Treat `current-state.md` as the single operational truth.
- Read `knowledge/project-architecture-hubs-clicks.md` first when you need to understand the product, app structure, models, routes, templates, signals, and operational caveats.
- Read `knowledge/testing-strategy-hubs-clicks.md` before adding or changing tests; it records the current 35-test baseline, command, conventions, and gaps.
- Prefer `ai-handoff.md` for the current operational truth.
- Prefer `implementation-log.md` for what was actually executed.
- Prefer `verification-report.md` for evidence and acceptance checks.
- Prefer `knowledge/` documents for reusable patterns across projects.
