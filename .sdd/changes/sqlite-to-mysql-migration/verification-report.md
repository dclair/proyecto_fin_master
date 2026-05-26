# Verification Report: SQLite to MySQL/MariaDB Migration

**Date:** 2026-05-25  
**Status:** Passed automated verification  
**Manual browser validation:** Pending

## Acceptance Criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| MySQL/MariaDB schema created | PASS | All migrations applied with `[X]` |
| Data imported | PASS | `Installed 574 object(s)` |
| Row counts preserved | PASS | 16/16 model counts matched |
| UTF-8 support | PASS | Database and key tables use `utf8mb4_unicode_ci` |
| Django system check | PASS | `System check identified no issues` |
| Test suite | PASS | `13 tests OK` |
| Key FK orphan checks | PASS | All checked orphan counts were `0` |
| Media path sanity check | PASS | Sampled media references had `0` missing files |
| Profile creation signal | PASS | New `User` created a `UserProfile` |
| Rollback path | PASS | `DB_ENGINE=sqlite` overrides `.env` |

## Data Counts

| Model | Count |
| --- | ---: |
| `admin.logentry` | 75 |
| `aficionados_network.contactmessage` | 5 |
| `auth.permission` | 76 |
| `auth.user` | 6 |
| `contenttypes.contenttype` | 19 |
| `flatpages.flatpage` | 2 |
| `notifications.notification` | 170 |
| `posts.comment` | 100 |
| `posts.event` | 24 |
| `posts.eventcomment` | 44 |
| `posts.posts` | 13 |
| `profiles.follow` | 10 |
| `profiles.hobby` | 4 |
| `profiles.review` | 11 |
| `profiles.userhobby` | 9 |
| `profiles.userprofile` | 6 |
| **Total** | **574** |

## Manual Browser Checklist

Use this checklist before declaring the migration fully production-validated.

- [ ] Open the home page.
- [ ] Log in with an existing user.
- [ ] Register a new user and confirm profile auto-creation.
- [ ] View and edit a profile.
- [ ] Follow and unfollow another profile.
- [ ] Create a post with and without an image.
- [ ] Like and comment on a post.
- [ ] Create an event.
- [ ] Join and leave an event.
- [ ] Cancel an event as organizer.
- [ ] Add/view event comments.
- [ ] Confirm notification bell count updates.
- [ ] Open notification links.
- [ ] Confirm profile, post, and event images render.
- [ ] Check `/admin/` loads and key models are visible.

## Useful Verification Commands

```bash
python manage.py check
python manage.py test
python manage.py showmigrations --plan
```

```bash
DB_ENGINE=sqlite python manage.py check
```

```sql
SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
FROM information_schema.SCHEMATA
WHERE SCHEMA_NAME='aficionados_network_db';
```

