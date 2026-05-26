# Proposal: SQLite → MySQL/MariaDB Migration

**Project:** Django Aficionados Network  
**Change Name:** `sqlite-to-mysql-migration`  
**Date:** 2026-05-25  
**Status:** Proposed  

---

## 1. Intent & Goals

### Why Migrate?

The Aficionados Network currently runs on SQLite, suitable for development and lightweight deployments. This proposal addresses the need for:

- **Production Readiness:** MySQL/MariaDB provides robust concurrent connection handling required for multi-user scenarios
- **Scalability:** Better resource management under load compared to file-based storage
- **Maintainability:** Familiar database engine with standard backup/restore workflows
- **Compatibility:** Aligns with industry standards for Django deployments
- **Infrastructure Flexibility:** Enables containerization and cloud deployment patterns

### Success Criteria

1. **Zero Data Loss** – All records, relationships, and constraints preserved exactly
2. **Schema Parity** – SQLite schema translates identically to MySQL without manual adjustments
3. **Validation Complete** – Data integrity verified post-migration (record counts, relationships, signals working)
4. **Rollback Capability** – SQLite backup retained for emergency recovery
5. **Performance Baseline** – No application speed regression after migration
6. **Documentation Updated** – Setup instructions reflect new database requirement

---

## 2. Scope

### What's IN

- **Data Migration:** All tables (users, posts, profiles, notifications, events, etc.)
- **Schema Elements:** Fields, types, constraints, indexes, relationships
- **Signals & Integrity:** Notification signals, profile auto-creation, follow relationships
- **File Uploads:** Media path handling (unchanged, but verified)
- **Fixture/Test Data:** Preserved for integration testing
- **Test Strategy:** Local validation before production cutover

### What's OUT

- **Application Code:** No models, views, or forms changes needed
- **API Contracts:** Endpoints and serialization remain unchanged
- **Frontend Changes:** Zero UI/UX modifications
- **Infrastructure Provisioning:** Assumes MariaDB available locally (user responsibility)
- **Docker/Deployment:** Not in this change scope (can follow separately)

---

## 3. Approach

### Five-Phase Execution Strategy

**Phase 1: Dependencies & Environment Setup**
- Install `mysqlclient` Python package (or `PyMySQL` fallback)
- Verify MariaDB is running locally
- Create database user and schema with appropriate privileges
- Validate connection from Django

**Phase 2: Settings Configuration**
- Update `settings.py` DATABASE config to point to MySQL
- Use environment variables (`.env`) for credentials (development practice)
- Keep SQLite config as fallback/secondary (initially)
- Run `python manage.py migrate` against new MySQL engine (creates schema)

**Phase 3: Data Migration (Dump → Restore Pattern)**
- Export all SQLite data: `./manage.py dumpdata > dump.json`
- Clear MySQL schema: `./manage.py flush --noinput` (safe on fresh schema)
- Import data: `./manage.py loaddata dump.json`
- Verify record counts match source

**Phase 4: Local Testing & Validation**
- Run Django test suite against MySQL backend
- Manually test critical workflows (user registration, post creation, notifications)
- Verify file uploads work with MySQL (media paths unchanged)
- Test signal propagation (notifications on follow/like/comment)
- Check data integrity (relationships, cascades, constraints)

**Phase 5: Cleanup & Verification**
- Disable SQLite config from settings
- Archive SQLite backup (`db.sqlite3.backup`)
- Update `requirements.txt` with MySQL driver
- Document new setup steps in README
- Verify CI/CD passes (if configured)

---

## 4. Why This Approach

### Safety & Reversibility
- **Dump/Restore Pattern:** Industry-standard for data migration; atomic, testable, reversible
- **Backup Retention:** SQLite file kept as insurance for 48 hours post-migration
- **No Code Changes:** ORM handles all database abstraction; only config changes needed

### Minimal Disruption
- **No Application Downtime:** Can run both databases simultaneously during testing
- **Zero Client Impact:** No API changes, endpoint URLs, or client-side code modifications
- **Environment-Driven:** Use `.env` for database selection; deploy when ready

### Django ORM Consistency
- Django's `dumpdata`/`loaddata` tools respect models and relationships
- Migrations already applied (schema created by ORM)
- Ensures no schema drift or undocumented dependencies

### Validation First
- Local testing catches issues (signal timing, encoding, constraints) before cutover
- CI/CD provides regression safety if configured

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Data Loss During Migration** | Critical | Full SQLite backup before any changes; record counts verified post-import |
| **File Upload Path Breakage** | High | Media directories unchanged in filesystem; test upload workflow locally |
| **Signal Timing with MySQL** | Medium | Run integration tests locally (follow creation, notifications); MySQL is faster |
| **UTF-8 Charset Mismatch** | Medium | Already configured `'OPTIONS': {'charset': 'utf8mb4'}` in dual-config ✅ |
| **Connection Pool Exhaustion** | Low | Local testing only; production scaling handled separately |
| **Existing Data Corruption (hidden)** | Low | SQLite validation script runs pre-migration to catch issues |
| **MariaDB Not Available** | High | User verifies MariaDB running before Phase 1 |

---

## 6. Key Decisions

### Database Driver: `mysqlclient` vs `PyMySQL`
- **Decision:** `mysqlclient` (primary) with `PyMySQL` fallback documented
- **Rationale:** `mysqlclient` is faster (C-based); `PyMySQL` is pure Python if needed
- **Implementation:** Try `mysqlclient` first; fallback noted in docs

### Backup Strategy
- **Decision:** Keep SQLite backup for 48 hours post-migration, then archive
- **Rationale:** Sufficient for rollback if critical issue discovered; doesn't clutter workspace long-term
- **File:** `db.sqlite3.backup` in project root

### Testing Scope
- **Decision:** Full integration test run locally before declaring success
- **Rationale:** Catches signal failures, encoding issues, constraint violations early
- **Coverage:** All app models (posts, profiles, notifications, events) + signal checks

### Credential Management
- **Decision:** Use `.env` file for DB credentials (development); production uses managed secrets
- **Rationale:** Aligns with 12-factor app principles; non-production data
- **File:** `.env` (added to `.gitignore`, not committed)

---

## 7. Estimated Effort

| Phase | Task | Estimate |
|-------|------|----------|
| **T0** | Install package, verify MariaDB connection | 20 min |
| **T1** | Update settings, test connection, run migrations | 15 min |
| **T2** | Dump SQLite, load into MySQL, verify counts | 5 min |
| **T3** | Run test suite, manual verification, signal testing | 30 min |
| **T4** | Cleanup, backup archival, docs update, final check | 10 min |
| | **TOTAL** | **~80 minutes (methodical pace)** |

---

## 8. Assumptions

1. **MariaDB is installed locally** and running (`mysql` command accessible)
2. **User has database admin privileges** (can create users, databases)
3. **Project has no custom database functions or triggers** (ORM-compatible)
4. **No existing multi-database read replicas** (single writer assumption)
5. **Test suite passes against current SQLite** (baseline established)
6. **File uploads are functional in current setup** (no media path issues to fix)
7. **Django version supports MySQL driver** (project dependencies allow)

---

## 9. Next Steps if Approved

If this proposal is accepted, the workflow proceeds as:

1. **Specification Phase** (`sdd-spec`)
   - Write detailed requirements and test scenarios
   - Document expected behavior for each phase
   - Define validation acceptance criteria

2. **Design Phase** (`sdd-design`)
   - Exact shell commands and scripts
   - SQL verification queries
   - Error handling and rollback procedures

3. **Tasks Breakdown** (`sdd-tasks`)
   - Checklist for each phase
   - Dependency sequence
   - Verification steps between tasks

4. **Implementation** (`sdd-apply`)
   - Execute tasks systematically
   - Log output and validate

5. **Verification** (`sdd-verify`)
   - Confirm proposal success criteria met
   - Document final state

6. **Archive** (`sdd-archive`)
   - Mark change complete
   - Archive artifacts and decisions

---

## 10. Decision Required

**DECISION POINT:**
- ✅ **APPROVE** – Proceed to Specification phase with this approach
- 🔄 **REVISE** – Adjust scope, phases, or assumptions
- ❌ **REJECT** – Use alternative approach (e.g., PostgreSQL, managed cloud DB)

---

*Proposal created: 2026-05-25 | Change: sqlite-to-mysql-migration | Ready for review*
