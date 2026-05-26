# Specification: SQLite → MySQL/MariaDB Migration

**Change:** `sqlite-to-mysql-migration`  
**Date:** 2026-05-25  
**Status:** SPECIFICATION PHASE  
**Target:** Migrate production database from SQLite to MySQL/MariaDB with zero data loss and full rollback capability.

---

## 1. FUNCTIONAL REQUIREMENTS

### 1.1 Database Setup & Configuration

**FR-1.1a: MySQL/MariaDB Database Creation**
- Create new MySQL database named `aficionados_network` (production name)
- Character set: `utf8mb4` (full Unicode support)
- Collation: `utf8mb4_unicode_ci` (case-insensitive, Unicode-safe)
- Command pattern:
  ```sql
  CREATE DATABASE aficionados_network 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;
  ```
- Verification: Query `information_schema.SCHEMATA` confirms encoding

**FR-1.1b: MySQL User & Permissions**
- Create dedicated Django user: `django_user`
- Host: `localhost` (local development), `127.0.0.1` as fallback
- Required permissions on `aficionados_network.*`:
  - `SELECT, INSERT, UPDATE, DELETE` (data operations)
  - `CREATE, ALTER, DROP` (migrations)
  - `INDEX` (for query optimization)
- NO global privileges (principle of least privilege)
- Command pattern:
  ```sql
  CREATE USER 'django_user'@'localhost' IDENTIFIED BY '{STRONG_PASSWORD}';
  GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX 
    ON aficionados_network.* 
    TO 'django_user'@'localhost';
  FLUSH PRIVILEGES;
  ```

**FR-1.1c: Connection Test**
- Run `python manage.py dbshell --database=mysql` to verify connectivity
- Expected output: MySQL command prompt or shell access
- Failure mode: Connection error indicates misconfig (credentials, host, permissions)

### 1.2 Environment Variables & Configuration

**FR-1.2a: Environment Variables** (stored in `.env`)
```
DB_ENGINE=mysql                    # Backend driver
DB_NAME=aficionados_network        # Database name
DB_USER=django_user                # Database user
DB_PASSWORD=<32-char-random>       # Strong password (generate fresh)
DB_HOST=127.0.0.1                  # Localhost or IP
DB_PORT=3306                       # MySQL default port
```

**FR-1.2b: Django Settings Integration**
- File: [aficionados_network/settings.py](aficionados_network/settings.py)
- Existing dual-DB configuration already present (verified in exploration)
- ENV-based selection:
  ```python
  DATABASES = {
      'default': { ... current_sqlite ... },
      'mysql': {
          'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
          'NAME': os.getenv('DB_NAME', 'db.sqlite3'),
          'USER': os.getenv('DB_USER', ''),
          'PASSWORD': os.getenv('DB_PASSWORD', ''),
          'HOST': os.getenv('DB_HOST', 'localhost'),
          'PORT': os.getenv('DB_PORT', '3306'),
          'OPTIONS': {
              'charset': 'utf8mb4',
              'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
          }
      }
  }
  ```
- Fallback: If env vars missing, defaults to SQLite (safe)

**FR-1.2c: Charset Configuration**
- Global: `DEFAULT CHARACTER SET utf8mb4` on database
- Connection: `SET NAMES utf8mb4` in Django OPTIONS
- Tables: Inherited from database charset
- Verification: `SHOW CREATE TABLE {table_name}` confirms `utf8mb4`

### 1.3 Driver Installation & Fallback

**FR-1.3a: Primary Driver – mysqlclient**
- Install: `pip install mysqlclient` (C-based, faster)
- Python binding: Cython wrapper around MySQL C connector
- Performance: ~3-5x faster than pure-Python alternatives
- Installation requirement: System MySQL dev headers (`libmysqlclient-dev` on Linux)
- Verification: `python -c "import MySQLdb"` succeeds

**FR-1.3b: Fallback Driver – PyMySQL**
- Install: `pip install PyMySQL` (pure Python, portable)
- Used if mysqlclient fails to compile or import
- Same API surface (Django-compatible)
- Performance: Acceptable for small-to-medium datasets
- Fallback activation:
  ```python
  try:
      import MySQLdb  # mysqlclient
  except ImportError:
      import pymysql
      pymysql.install_as_MySQLdb()
  ```

**FR-1.3c: Requirements File Update**
- File: [requirements.txt](requirements.txt)
- Add: `mysqlclient==1.4.6` (or latest stable)
- OR: `PyMySQL==1.1.0` (fallback explicit option)
- Fresh install: `pip install -r requirements.txt`

### 1.4 Connection Pooling

**FR-1.4a: Initial Connection Pool Configuration**
- Connection pool size: `CONN_MAX_AGE = 600` (10 minutes, default)
- Strategy: Simple age-based pool (Django built-in)
- Reasoning: Adequate for development; premature optimization avoided
- Configuration in settings.py:
  ```python
  DATABASES['mysql']['CONN_MAX_AGE'] = 600
  ```

**FR-1.4b: Pool Monitoring**
- Max connections per Django: 10 (default database thread limit)
- Overflow handling: MySQL server rejects excess connections
- Monitoring: Check MySQL `SHOW PROCESSLIST` to observe connection count
- Scaling: Connection pooling can be optimized in design phase (e.g., django-db-pool)

---

## 2. DATA REQUIREMENTS

### 2.1 Data Preservation & Validation

**DR-2.1a: 100% Row Count Match**
- SQLite → JSON dump → MySQL load
- Validation: Query both databases, compare row counts per table
- Tables to verify (complete list):
  - `auth_user` (Django built-in)
  - `auth_group` (Django built-in)
  - `auth_permission` (Django built-in)
  - `posts_posts`
  - `posts_comment`
  - `posts_category`
  - `posts_event`
  - `posts_eventcomment`
  - `profiles_userprofile`
  - `profiles_hobby`
  - `profiles_userhobby`
  - `profiles_follow`
  - `profiles_review`
  - `notifications_notification`
  - `aficionados_network_contactmessage`
  - All M2M junction tables (auto-generated by Django)
- Failure criteria: Any mismatch indicates corruption

**DR-2.1b: Null & Default Value Preservation**
- SQLite NULL → MySQL NULL (preserved exactly)
- Default values: Auto-generated on INSERT (timestamps, auto-increment)
- Exclusion: `auto_now_add` and `auto_now` fields regenerate on load (expected)
- Verification: Sample rows from source and target, compare field-by-field

**DR-2.1c: No Orphaned Records**
- Cascading deletes verified: No FK violations post-load
- Query pattern: `SELECT * FROM {child_table} WHERE {fk_id} NOT IN (SELECT id FROM {parent_table})`
- Expected result: Empty (0 rows)
- Tables to check:
  - `posts_comment` → `posts_posts` (FK: post_id)
  - `posts_eventcomment` → `posts_event` (FK: event_id)
  - `posts_event` → `profiles_hobby` (FK: hobby_id)
  - `posts_event` → `auth_user` (FK: organizer_id)
  - `notifications_notification` → `auth_user` (FK: recipient_id)
  - `profiles_review` → `posts_event` (FK: event_id)

### 2.2 Schema Integrity

**DR-2.2a: Table & Column Structure Match**
- All 15+ core tables present in MySQL
- Column count per table matches SQLite
- Column types compatible or upgraded:
  - `AutoField` (SQLite) → `BigAutoField` (MySQL) ✅ Compatible
  - `CharField(max_length)` → `VARCHAR(max_length)` ✅ Preserved
  - `TextField` → `LONGTEXT` ✅ Compatible
  - `DateTimeField` → `DATETIME(6)` ✅ Preserves microseconds
  - `BooleanField` → `TINYINT(1)` ✅ Standard
  - `ImageField` → `VARCHAR(100)` ✅ Path storage

**DR-2.2b: Constraints Preservation**
- **Unique constraints:**
  - `posts_posts.slug` (UNIQUE)
  - `profiles_hobby.name` (UNIQUE)
  - `profiles_hobby.slug` (UNIQUE)
  - `profiles_userhobby(profile_id, hobby_id)` (composite UNIQUE)
  - `profiles_follow(follower_id, following_id)` (composite UNIQUE)
  - `profiles_review(event_id, author_id)` (composite UNIQUE)
- Verification: Try duplicate insert → Expect constraint error

- **Foreign Keys:**
  - All FKs present with ON DELETE CASCADE behavior
  - Referential integrity enforced in MySQL (unlike SQLite without PRAGMA)
  - Verification: Query `information_schema.KEY_COLUMN_USAGE`

- **Primary Keys:**
  - All tables have `id` as BigAutoField (auto-increment)
  - MySQL AUTOINCREMENT preserved from JSON dump
  - Verification: Insert new row → auto-assigned ID continues sequence

**DR-2.2c: Indexes**
- All Django-generated indexes present
- FK indexes auto-created (MySQL behavior)
- Unique constraint indexes verified
- Performance: MySQL indexes more efficient than SQLite

### 2.3 Cascading Delete Behavior

**DR-2.3a: FK Relationships with ON DELETE CASCADE**
- Django ORM default: `on_delete=models.CASCADE`
- SQLite: Cascading deletes require `PRAGMA foreign_keys = ON`
- MySQL: Cascades enforced by default (safer)

**DR-2.3b: Test Scenarios**
- Delete `Posts` instance → `Comment` records auto-deleted
- Delete `User` → `UserProfile` cascade via O2O
- Delete `Event` → `Review`, `EventComment` deleted
- Delete `UserProfile` → `Follow` (as follower or following) deleted

---

## 3. VALIDATION SCENARIOS

### 3.1 Schema Integrity (YES/NO)

**S1: Schema Matches**

```gherkin
SCENARIO: Verify all tables and columns are present in MySQL

GIVEN:
  - SQLite source database with 29 migrations applied
  - MySQL target database created with UTF8MB4 charset
  - Both databases accessible via Django ORM

WHEN:
  - Running: python manage.py inspect_db
  - Comparing table structure (via information_schema.TABLES)
  - Comparing column definitions (via information_schema.COLUMNS)
  - Comparing constraints (via information_schema.KEY_COLUMN_USAGE)

THEN:
  - ✅ All 15+ core tables exist in MySQL
  - ✅ Each table has identical column count and names
  - ✅ Column types compatible or upgraded (SQLite → MySQL)
  - ✅ All PRIMARY KEY, FOREIGN KEY, UNIQUE constraints present
  - ✅ All indexes present (including composite FK indexes)
  - ✅ DEFAULT values and AUTO_INCREMENT configured correctly

FAILURE CRITERIA:
  - ❌ Missing table
  - ❌ Missing column
  - ❌ Type mismatch (e.g., INTEGER vs VARCHAR)
  - ❌ Missing constraint
  - ❌ AUTO_INCREMENT sequence broken
```

**Verification Queries:**
```sql
-- Check table count
SELECT COUNT(*) AS table_count FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'aficionados_network';

-- Check specific table structure
DESCRIBE posts_posts;

-- Check constraints
SELECT * FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = 'aficionados_network';

-- Check AUTO_INCREMENT status
SHOW TABLE STATUS FROM aficionados_network WHERE Name = 'posts_posts'\G
```

---

### 3.2 Data Integrity (YES/NO)

**S2: Data Integrity – Row Counts**

```gherkin
SCENARIO: Verify 100% data transfer with no losses

GIVEN:
  - SQLite database with existing data (posts, users, profiles, etc.)
  - MySQL empty database after schema migration
  - Valid dumpdata JSON file created from SQLite

WHEN:
  - Running: python manage.py dumpdata > db_backup.json
  - Running: python manage.py loaddata db_backup.json --database=mysql
  - Comparing row counts: SELECT COUNT(*) FROM {table}

THEN:
  - ✅ Row count for each table MATCHES between SQLite source and MySQL target
  - ✅ No data corruption in JSON dump (valid JSON syntax)
  - ✅ No duplicate rows after load
  - ✅ No missing rows
  - ✅ All M2M junction tables loaded correctly

FAILURE CRITERIA:
  - ❌ Row count mismatch in any table
  - ❌ Invalid JSON dump
  - ❌ Load operation fails with "Duplicate entry" error
  - ❌ Orphaned records present (see S2b below)

TEST DATA EXPECTED:
  - posts_posts: ~20-50 rows (depends on development data)
  - auth_user: ~5-20 rows
  - profiles_userprofile: 1:1 with auth_user
  - profiles_follow: depends on test data (0-100 rows)
  - notifications_notification: depends on activity (0-500 rows)
```

**Verification Queries:**
```sql
-- Row count comparison (run on both SQLite and MySQL)
SELECT 'posts_posts' AS table_name, COUNT(*) AS row_count FROM posts_posts
UNION ALL
SELECT 'posts_comment', COUNT(*) FROM posts_comment
UNION ALL
SELECT 'profiles_userprofile', COUNT(*) FROM profiles_userprofile
UNION ALL
SELECT 'profiles_follow', COUNT(*) FROM profiles_follow
UNION ALL
SELECT 'notifications_notification', COUNT(*) FROM notifications_notification;
```

**S2b: Data Integrity – No Orphaned Records**

```gherkin
SCENARIO: Verify no orphaned records (broken FK references)

GIVEN:
  - MySQL database loaded with dumpdata
  - All FK relationships defined with ON DELETE CASCADE

WHEN:
  - Querying child tables for orphaned records
  - Example: comments referring to deleted posts

THEN:
  - ✅ posts_comment has NO records where post_id doesn't exist in posts_posts
  - ✅ posts_event has NO records where organizer_id doesn't exist in auth_user
  - ✅ profiles_review has NO records where event_id doesn't exist in posts_event
  - ✅ notifications_notification has NO records where recipient_id doesn't exist in auth_user

FAILURE CRITERIA:
  - ❌ Found orphaned child records (FK violation)
  - ❌ Referential integrity error
```

**Verification Query Pattern:**
```sql
-- Detect orphaned comments
SELECT c.id FROM posts_comment c
WHERE c.post_id NOT IN (SELECT id FROM posts_posts);
-- Expected: EMPTY RESULT SET (0 rows)

-- Detect orphaned events
SELECT e.id FROM posts_event e
WHERE e.organizer_id NOT IN (SELECT id FROM auth_user)
   OR e.hobby_id NOT IN (SELECT id FROM profiles_hobby);
-- Expected: EMPTY RESULT SET
```

---

### 3.3 Cascading Delete Behavior (YES/NO)

**S3: Cascading Deletes Work Correctly**

```gherkin
SCENARIO: Verify that deleting a parent record cascades to child records

GIVEN:
  - MySQL database with loaded data
  - A Post with associated Comments and Notifications
  - ON DELETE CASCADE configured on FKs

WHEN:
  - Deleting the Post via Django ORM: post.delete()
  - OR: DELETE FROM posts_posts WHERE id = {post_id};

THEN:
  - ✅ Post deleted from posts_posts
  - ✅ All associated Comments auto-deleted from posts_comment
  - ✅ All associated Notifications auto-deleted from notifications_notification
  - ✅ No orphaned records remain
  - ✅ Row count decreases correctly

FAILURE CRITERIA:
  - ❌ Post deleted but Comments remain (orphaned)
  - ❌ Referential integrity error on delete attempt
  - ❌ Manual cascading required (should be automatic)
```

**Test Scenario:**
```python
# Python test code
post = Posts.objects.using('mysql').first()
comment_ids = list(post.comment_set.values_list('id', flat=True))
post.delete(using='mysql')

# Verify comments are gone
remaining = Comment.objects.using('mysql').filter(id__in=comment_ids).count()
assert remaining == 0  # ✅ All cascaded
```

**SQL Verification:**
```sql
-- Before delete: Count related records
SELECT COUNT(*) FROM posts_comment WHERE post_id = 5;  -- e.g., 3 comments

-- After delete
DELETE FROM posts_posts WHERE id = 5;
SELECT COUNT(*) FROM posts_comment WHERE post_id = 5;  -- MUST be 0
```

---

### 3.4 Many-to-Many Relationships (YES/NO)

**S4: M2M Relationships Preserved**

```gherkin
SCENARIO: Verify through-tables transfer correctly with proper relationships

GIVEN:
  - SQLite data with M2M relationships:
    - UserProfile.hobbies (via profiles_userhobby through-table)
    - UserProfile.followers/following (via profiles_follow through-table)
    - Posts.likes (via posts_posts_likes junction table)
    - Event.participants (via posts_event_participants junction table)

WHEN:
  - Loading dumpdata into MySQL
  - Querying M2M relationships via Django ORM

THEN:
  - ✅ profiles_userhobby rows match source count
  - ✅ profiles_follow rows match source count
  - ✅ Querying user.hobbies.all() returns same hobby set
  - ✅ Querying user.following.all() returns same users
  - ✅ posts_posts_likes rows correct
  - ✅ event.participants.all() returns same participants
  - ✅ No duplicate entries in junction tables

FAILURE CRITERIA:
  - ❌ Through-table rows lost or duplicated
  - ❌ M2M query returns wrong set
  - ❌ Composite UNIQUE constraints violated
```

**Test Scenario:**
```python
# Django ORM test
user_sqlite = UserProfile.objects.using('default').first()
user_mysql = UserProfile.objects.using('mysql').filter(id=user_sqlite.id).first()

hobbies_sqlite = set(user_sqlite.hobbies.values_list('id', flat=True))
hobbies_mysql = set(user_mysql.hobbies.values_list('id', flat=True))

assert hobbies_sqlite == hobbies_mysql  # ✅ Same hobbies
```

**SQL Verification:**
```sql
-- Check UserHobby through-table
SELECT COUNT(*) FROM profiles_userhobby;

-- Verify no duplicates (composite UNIQUE should prevent this)
SELECT profile_id, hobby_id, COUNT(*) 
FROM profiles_userhobby 
GROUP BY profile_id, hobby_id 
HAVING COUNT(*) > 1;
-- Expected: EMPTY RESULT SET
```

---

### 3.5 Signal Handlers (YES/NO)

**S5: Signals Fire Correctly During Data Load**

```gherkin
SCENARIO: Verify Django signal handlers work with MySQL backend

GIVEN:
  - Django signals configured in profiles/signals.py and notifications/signals.py
  - Key signal: post_save(sender=User) → auto-create UserProfile (O2O)
  - Database operations use MySQL backend

WHEN:
  - Creating a new User via Django ORM: User.objects.create(...)
  - OR: Loading existing users via loaddata

THEN:
  - ✅ post_save signal fires on create
  - ✅ UserProfile auto-created linked to User (1:1 relationship)
  - ✅ Signal transactions complete successfully
  - ✅ No double-creation issues
  - ✅ UserProfile.id matches User.id (O2O pattern)

FAILURE CRITERIA:
  - ❌ UserProfile not auto-created for new User
  - ❌ Duplicate UserProfile (signal fired twice)
  - ❌ Transaction rolled back due to signal exception
  - ❌ Signal fails silently (logs required to detect)

CONTEXT (from code):
  File: profiles/signals.py
  - Signal: post_save, sender=User
  - Handler: creates UserProfile with User.id as PK
  - Atomic: Within transaction (loaddata wraps in transaction)
```

**Test Scenario:**
```python
# Create new user on MySQL
new_user = User.objects.create_user(
    username='test_signal',
    email='test@example.com',
    using='mysql'
)

# Verify UserProfile auto-created
profile = UserProfile.objects.using('mysql').get(user_id=new_user.id)
assert profile is not None  # ✅ Signal fired
```

---

### 3.6 File Uploads & Media Access (YES/NO)

**S6: File Uploads Accessible at Identical Paths**

```gherkin
SCENARIO: Verify media files (post images, profile pics) remain accessible

GIVEN:
  - SQLite database with Posts containing image references
  - Posts.image field pointing to files in MEDIA_ROOT/posts_images/
  - UserProfile.profile_picture field in MEDIA_ROOT/profile_pics/
  - Media files physically present on filesystem

WHEN:
  - Switching DATABASE from SQLite to MySQL
  - Querying Posts and UserProfile for image paths
  - Accessing media via web (DEBUG=True)

THEN:
  - ✅ Posts.image.url returns correct path (unchanged)
  - ✅ UserProfile.profile_picture.url returns correct path
  - ✅ Files exist at MEDIA_ROOT + stored path
  - ✅ File permissions unchanged (readable)
  - ✅ Web server can serve media files
  - ✅ No database errors fetching image field values

FAILURE CRITERIA:
  - ❌ Image path lost or corrupted in transfer
  - ❌ File not found at expected path
  - ❌ File permissions broken (permission denied)
  - ❌ NULL image values where files should exist

CONTEXT (from codebase):
  File: posts/models.py
  - Posts.image: ImageField(upload_to='posts_images/%Y/')
  File: profiles/models.py
  - UserProfile.profile_picture: ImageField(upload_to='profile_pics/')
```

**Verification Queries & Code:**
```sql
-- Check image field values
SELECT id, image FROM posts_posts WHERE image IS NOT NULL LIMIT 5;

-- Verify files exist
SELECT id, profile_picture FROM profiles_userprofile 
WHERE profile_picture IS NOT NULL LIMIT 5;
```

**Python Verification:**
```python
import os
from django.conf import settings

posts = Posts.objects.using('mysql').filter(image__isnull=False)
for post in posts[:5]:
    file_path = os.path.join(settings.MEDIA_ROOT, post.image.name)
    assert os.path.exists(file_path), f"File missing: {file_path}"
    # ✅ File accessible
```

---

### 3.7 Unique Constraints Enforced (YES/NO)

**S7: Unique Constraints Prevent Duplicates**

```gherkin
SCENARIO: Verify UNIQUE constraints enforced at database level

GIVEN:
  - MySQL database with loaded data
  - UNIQUE constraints on:
    - posts_posts.slug
    - profiles_hobby.name
    - profiles_hobby.slug
    - Composite: (profile_id, hobby_id) in profiles_userhobby
    - Composite: (follower_id, following_id) in profiles_follow
    - Composite: (event_id, author_id) in profiles_review

WHEN:
  - Attempting to insert duplicate slug: INSERT INTO posts_posts (slug, ...) VALUES ('existing-slug', ...)
  - Attempting to insert duplicate hobby: INSERT INTO profiles_hobby (name, ...) VALUES ('existing-name', ...)
  - Attempting duplicate M2M: INSERT INTO profiles_userhobby VALUES (user_id, hobby_id, ...)

THEN:
  - ✅ MySQL rejects insert with error: "Duplicate entry"
  - ✅ IntegrityError raised in Django ORM
  - ✅ Transaction rolled back automatically
  - ✅ No partial data inserted

FAILURE CRITERIA:
  - ❌ Duplicate insert succeeds (constraint not enforced)
  - ❌ No error raised
  - ❌ Silent data duplication

CONTEXT (from codebase):
  File: posts/models.py
  - Posts.slug: SlugField(unique=True)
  File: profiles/models.py
  - Hobby.name: CharField(unique=True)
  - Hobby.slug: SlugField(unique=True)
  - UserHobby: Meta.unique_together = [('profile', 'hobby')]
  - Follow: Meta.unique_together = [('follower', 'following')]
```

**Test Scenario:**
```python
from django.db import IntegrityError

# Test Posts.slug unique constraint
post1 = Posts.objects.create_using('mysql')(title='Post 1', slug='my-post', ...)
try:
    post2 = Posts.objects.create_using('mysql')(title='Post 2', slug='my-post', ...)
    assert False, "Should have raised IntegrityError"
except IntegrityError:
    pass  # ✅ Constraint enforced

# Test Hobby.name unique constraint
hobby1 = Hobby.objects.using('mysql').create(name='Coding', ...)
try:
    hobby2 = Hobby.objects.using('mysql').create(name='Coding', ...)
    assert False, "Duplicate hobby name should fail"
except IntegrityError:
    pass  # ✅ Constraint enforced
```

**SQL Verification:**
```sql
-- Try duplicate slug
INSERT INTO posts_posts (slug, title, user_id, created_at, updated_at)
VALUES ('existing-slug', 'Test Post', 1, NOW(), NOW());
-- Expected: ERROR 1062 (23000): Duplicate entry 'existing-slug' for key 'posts_posts.slug'
```

---

### 3.8 Timezone Integrity (YES/NO)

**S8: Timezone-Aware Datetimes Preserved**

```gherkin
SCENARIO: Verify datetime fields preserve timezone information

GIVEN:
  - Django setting: USE_TZ=True
  - TIME_ZONE='UTC'
  - SQLite datetimes stored as UTC strings
  - DateTimeField values in Posts, Comments, Events, etc.
  - auto_now_add and auto_now fields present

WHEN:
  - Transferring datetime data to MySQL via dumpdata/loaddata
  - Querying datetime fields from MySQL
  - Comparing timestamps: source vs. target

THEN:
  - ✅ All datetime values preserved exactly (UTC)
  - ✅ No timezone conversion artifacts
  - ✅ auto_now_add timestamps match source (when loaded)
  - ✅ Microseconds preserved (DATETIME(6) in MySQL)
  - ✅ Querying via Django ORM returns timezone-aware datetime
  - ✅ Serialization to JSON consistent across backends

FAILURE CRITERIA:
  - ❌ Datetime values shifted (e.g., +/- hours)
  - ❌ Timezone information lost
  - ❌ Microseconds truncated
  - ❌ NULL datetimes where values should exist

CONTEXT (from codebase):
  File: aficionados_network/settings.py
  - USE_TZ = True
  - TIME_ZONE = 'UTC'
  File: posts/models.py, profiles/models.py, etc.
  - created_at: DateTimeField(auto_now_add=True)
  - updated_at: DateTimeField(auto_now=True)
```

**Verification Queries:**
```python
# Compare timestamps across backends
import pytz
from datetime import datetime

post_sqlite = Posts.objects.using('default').first()
post_mysql = Posts.objects.using('mysql').filter(id=post_sqlite.id).first()

# Check created_at
sqlite_tz = post_sqlite.created_at.replace(tzinfo=pytz.UTC) if post_sqlite.created_at else None
mysql_tz = post_mysql.created_at.replace(tzinfo=pytz.UTC) if post_mysql.created_at else None

assert sqlite_tz == mysql_tz, f"Mismatch: {sqlite_tz} vs {mysql_tz}"
# ✅ Timezones match
```

**SQL Verification:**
```sql
-- Check datetime precision
SHOW CREATE TABLE posts_posts\G
-- Expected: created_at DATETIME(6) with CURRENT_TIMESTAMP(6)

-- Sample datetime value
SELECT id, created_at, UNIX_TIMESTAMP(created_at) FROM posts_posts LIMIT 1;
```

---

### 3.9 Rollback Viability (YES/NO)

**S9: Rollback to SQLite Works Identically**

```gherkin
SCENARIO: Verify SQLite backup can be restored and application functions

GIVEN:
  - SQLite backup file: db.sqlite3.backup created pre-migration
  - Backup timestamp and MD5 checksum recorded
  - MySQL migration completed and tested

WHEN:
  - Delete or rename MySQL database
  - Restore db.sqlite3.backup → db.sqlite3
  - Switch DATABASE in settings (or .env) back to SQLite
  - Restart Django application

THEN:
  - ✅ SQLite database opens without errors
  - ✅ All tables present with original schema
  - ✅ All row counts match pre-migration state
  - ✅ Django migrations status shows "applied" (no pending)
  - ✅ Application runserver works
  - ✅ All data queries return expected results
  - ✅ No differences between original and restored SQLite

FAILURE CRITERIA:
  - ❌ SQLite database corrupted or won't open
  - ❌ Backup file MD5 mismatch (file corrupted)
  - ❌ Row counts don't match original
  - ❌ Django migrations status inconsistent
  - ❌ Application fails to start after restore

CONTEXT:
  Pre-migration:
  - Copy: cp db.sqlite3 db.sqlite3.backup
  - Record: md5sum db.sqlite3 > db.sqlite3.md5
  - Keep for 48 hours post-migration

Recovery process:
  - Restore: cp db.sqlite3.backup db.sqlite3
  - Verify: md5sum -c db.sqlite3.md5
  - Switch .env: DB_ENGINE=sqlite3
  - Restart app
```

**Verification Commands:**
```bash
# Pre-migration
cp db.sqlite3 db.sqlite3.backup
md5sum db.sqlite3 > db.sqlite3.md5

# Post-migration test (rollback scenario)
# 1. Backup MySQL (optional)
# 2. Delete or rename MySQL database
# 3. Restore SQLite
cp db.sqlite3.backup db.sqlite3

# 4. Verify integrity
md5sum -c db.sqlite3.md5

# 5. Check Django
python manage.py showmigrations  # Should show all applied

# 6. Count rows
python manage.py dbshell
> SELECT COUNT(*) FROM posts_posts;
# Compare with pre-migration count
```

---

### 3.10 Application Works on MySQL (YES/NO)

**S10: Full Django Application Runs on MySQL**

```gherkin
SCENARIO: Verify entire Django application functions correctly with MySQL backend

GIVEN:
  - MySQL database populated with migrated data
  - All Django migrations applied
  - Environment configured to use MySQL (DB_ENGINE=mysql)
  - settings.py dual-DB config active

WHEN:
  - Running: python manage.py runserver
  - Running full test suite: python manage.py test --database=mysql
  - Executing common operations: list posts, create profile, follow user, etc.

THEN:
  - ✅ Django runserver starts without errors
  - ✅ No database connection errors
  - ✅ All app views load successfully (no 500 errors)
  - ✅ All test cases pass against MySQL
  - ✅ Create/Update/Delete operations work
  - ✅ Complex queries (filters, aggregations) execute correctly
  - ✅ M2M operations (add/remove hobbies) work
  - ✅ Signals fire on create/update/delete
  - ✅ No race conditions or deadlocks
  - ✅ Admin panel works
  - ✅ ORM queries return correct results

FAILURE CRITERIA:
  - ❌ Django fails to connect to MySQL
  - ❌ Test suite has failures
  - ❌ Views return 500 errors
  - ❌ Database-specific SQL errors
  - ❌ ORM operations fail

TEST CHECKLIST:
  - [ ] python manage.py runserver → OK
  - [ ] python manage.py check --database=mysql → OK
  - [ ] python manage.py test --database=mysql → 100% pass
  - [ ] Admin login → OK
  - [ ] Browse posts list → OK
  - [ ] Create new post → OK
  - [ ] Follow user → OK
  - [ ] Create event → OK
  - [ ] Leave comment → OK
```

---

## 4. NON-FUNCTIONAL REQUIREMENTS

### NFR-4.1 Performance

**NFR-4.1a: Migration Execution Time**
- Target: Complete data dump and load in **<5 seconds**
- Measured: time span from `dumpdata` start to `loaddata` completion
- Affected by:
  - Data volume (small dataset → fast)
  - Disk I/O (SSD faster than HDD)
  - Network (localhost → no latency)
- Acceptable range: 3-8 seconds
- If >10 seconds: Investigate for issues (charset mismatch, missing index, etc.)

**NFR-4.1b: Query Performance Post-Migration**
- SQLite vs MySQL performance not tested (out of scope for this migration)
- Note: MySQL generally faster for concurrent access; SQLite adequate for dev
- Optimization: Can be addressed in future optimization phase

### NFR-4.2 Reversibility

**NFR-4.2a: One-Click Rollback**
- Rollback achievable in <2 minutes:
  1. Delete MySQL database (30 sec)
  2. Restore SQLite backup (10 sec)
  3. Update .env or settings (10 sec)
  4. Restart application (30 sec)
- Prerequisite: SQLite backup file kept for 48 hours
- No manual data recovery steps required

**NFR-4.2b: Data Preservation During Rollback**
- SQLite backup MD5-verified before/after rollback
- Zero data loss guarantee: All rows and values identical to pre-migration state
- No partial rollbacks: All-or-nothing (transaction-like semantics)

### NFR-4.3 Safety & Data Loss Prevention

**NFR-4.3a: Zero Data Loss**
- Validation steps ensure:
  - Row count match (before migration, after migration, post-rollback)
  - Orphaned record check (no broken FK references)
  - Unique constraint verification
  - Datetime integrity preserved
- Pre-migration: Full SQLite backup created and MD5-verified
- Post-migration: Duplicate row count validation

**NFR-4.3b: No Application Changes Required**
- All changes are configuration-only:
  - .env variables added
  - requirements.txt updated (driver)
  - Django settings already support dual-DB (no code changes)
- Application code remains identical (SQLite → MySQL swap is transparent)

### NFR-4.4 Documentation

**NFR-4.4a: Migration Steps Documented**
- Clear, step-by-step commands in design phase
- Each command includes:
  - Purpose (what it does)
  - Expected output (how to verify success)
  - Failure troubleshooting

**NFR-4.4b: Environment Variables Documented**
- All required .env variables listed
- Example values provided (with placeholders for secrets)
- Permission requirements documented
- Fallback options documented

**NFR-4.4c: Validation Procedure Documented**
- All 10 validation scenarios have SQL queries or Python tests
- Row count comparison template provided
- Rollback instructions explicit

### NFR-4.5 Compatibility

**NFR-4.5a: Python Version**
- Target: Python 3.12 (confirmed in workspace)
- mysqlclient: Compatible with 3.8+
- PyMySQL: Compatible with 3.7+
- ✅ No version conflicts

**NFR-4.5b: Django Version**
- Target: Django 6.0 (confirmed in requirements)
- MySQL backend: Stable and tested in Django 6.0
- Dual-DB config: Supported natively
- ✅ No version conflicts

**NFR-4.5c: MySQL/MariaDB Versions**
- Minimum: MySQL 5.7 OR MariaDB 10.5 (charset, JSON support)
- Tested: MariaDB 10.5+ (commonly available on Linux)
- Features used: None that require MySQL 8.0+
- ✅ Broad compatibility

---

## 5. DEPENDENCIES & ASSUMPTIONS

### 5.1 Required Dependencies

**DEP-5.1a: MySQL/MariaDB Installation**
- MUST be installed and running locally
- MUST be accessible on localhost:3306 or 127.0.0.1:3306
- MUST have user creation and database permissions (root or admin user)
- Verification: `mysql -u root -p -e "SELECT VERSION();"`
- If missing: Install (not in scope of this change; user responsibility)

**DEP-5.1b: mysqlclient Driver**
- MUST install: `pip install mysqlclient`
- Requires: MySQL dev headers (libmysqlclient-dev on Linux)
- If build fails: Fallback to `pip install PyMySQL`
- Verification: `python -c "import MySQLdb"` or `import pymysql`

**DEP-5.1c: Django & Dual-DB Config**
- MUST be: Django 6.0+ (confirmed present)
- MUST have: Dual-DB config in settings.py (confirmed present)
- MUST have: .env support via python-dotenv (confirmed present)

### 5.2 Assumed Pre-Conditions

**ASSUME-5.2a: All Migrations Applied**
- ASSUMPTION: All 29 Django migrations already applied to SQLite
- Verification: `python manage.py showmigrations` shows all checked
- If violated: Run `python manage.py migrate` first

**ASSUME-5.2b: No Pending Django Migrations**
- ASSUMPTION: No uncommitted migrations in migration files
- Verification: `python manage.py makemigrations --dry-run` returns nothing
- If violated: Commit pending migrations or rollback migrations

**ASSUME-5.2c: File Upload Permissions**
- ASSUMPTION: MEDIA_ROOT directory has same permissions on both systems
- ASSUMPTION: All post images and profile pictures accessible and not corrupted
- Verification: `ls -la media/posts_images/` and `media/profile_pics/`

**ASSUME-5.2d: No Raw SQL**
- ASSUMPTION: No database-specific SQL in codebase (verified in exploration)
- Verified: No raw SQL queries in views, managers, signals, fixtures
- Assumption allows safe migration without code changes

**ASSUME-5.2e: No Database-Specific Managers**
- ASSUMPTION: No custom managers using SQLite-only functions (verified)
- ASSUMPTION: All ORM operations are database-agnostic

### 5.3 Non-Blocking Assumptions (Can Proceed)

**NOBLOCK-5.3a: Dual-DB Config Works**
- The dual-DB configuration in settings.py is assumed to work
- If not: Can be debugged after migration via `python manage.py dbshell --database=mysql`

---

## 6. BLOCKERS & CRITICAL DECISIONS

### 6.1 Critical Decisions

**DECISION-6.1a: Use dump/restore Pattern (NOT Django Migration Backend Swap)**

**Choice:** `dumpdata` → JSON file → `loaddata` to MySQL

**Why:**
- ✅ Simpler: 2 commands, no config changes needed
- ✅ Safer: Data is "offline" in JSON format, can verify integrity before load
- ✅ Reversible: JSON can be reused if MySQL loads fail
- ✅ Zero app code changes: Only .env and requirements changes
- ✅ Faster: <5 seconds total
- ✅ Familiar: Standard Django backup/restore approach

**Alternative Rejected:** Django database backend swap (add MySQL to DATABASES, migrate --database=mysql)
- ❌ Riskier: Active data copy with concurrent writes possible
- ❌ Complex: Requires settings changes and multiple command sequence
- ❌ Less reversible: No off-database checkpoint
- ❌ Slower: Migrations run on every load (applies all 29 migrations)

**Decision Rationale:** Safety and simplicity trump speed for this small dataset. The 5-second difference is negligible.

---

**DECISION-6.1b: Keep SQLite Backup for 48 Hours Post-Migration**

**Choice:** Retain `db.sqlite3.backup` file for 2 days before deletion

**Why:**
- ✅ Instant rollback: If MySQL fails post-migration, rollback is <2 min
- ✅ Verification: Can compare data against backup if issues arise
- ✅ Low cost: Single file (small size, <100MB typically)
- ✅ Peace of mind: Reduces rollback anxiety

**Alternative Rejected:** Delete immediately post-migration
- ❌ Risky: If MySQL problem found later, rollback requires restore from time-machine backup (slow)
- ❌ Unforgiving: No margin for error
- ❌ Pressure: Forces decision-making under stress

**Decision Rationale:** 48-hour retention is a low-cost safety valve. Deletion can be scheduled automatically.

---

**DECISION-6.1c: mysqlclient as Primary, PyMySQL as Fallback**

**Choice:** Try mysqlclient; if import/build fails, use PyMySQL

**Why:**
- ✅ mysqlclient performance: 3-5x faster than PyMySQL (C-based)
- ✅ mysqlclient stable: Widely used in production
- ✅ PyMySQL fallback: Pure Python, no compilation issues, same API
- ✅ Portability: Can test on systems without MySQL dev headers

**Alternative Rejected:** PyMySQL only
- ❌ Performance: Slower for large datasets (not critical here, but sub-optimal)
- ❌ Lost opportunity: mysqlclient is industry standard

**Decision Rationale:** Pragmatic: Try best option first, have safe fallback.

---

**DECISION-6.1d: No Connection Pooling Optimization (Keep Simple)**

**Choice:** Use Django default CONN_MAX_AGE=600 (age-based pool)

**Why:**
- ✅ Sufficient: For development and small concurrent users
- ✅ Simple: Built-in, no external library required
- ✅ Debuggable: Django-native, easier troubleshooting
- ✅ Future-proof: Can upgrade to django-db-pool later if needed

**Alternative Rejected:** Complex pooling (django-db-pool, pgbouncer)
- ❌ Premature optimization: Not needed for this dataset
- ❌ Added complexity: More to configure and debug
- ❌ Overkill: Scaling concern, not migration concern

**Decision Rationale:** YAGNI principle. Add complexity only when needed (e.g., at 100+ concurrent users).

---

### 6.2 Potential Blockers

**BLOCKER-6.2a: MySQL Not Installed**
- Symptom: `mysql -u root -p` fails with "command not found"
- Resolution: Install MySQL/MariaDB (user responsibility)
- Impact: Blocks entire migration
- Mitigation: Pre-migration checklist includes verification

**BLOCKER-6.2b: mysqlclient Build Failure**
- Symptom: `pip install mysqlclient` fails with compiler error
- Resolution: Install MySQL dev headers (`libmysqlclient-dev` on Linux), or use PyMySQL fallback
- Impact: None (fallback available)
- Mitigation: Build instructions provided in design phase

**BLOCKER-6.2c: Insufficient Database Permissions**
- Symptom: CREATE DATABASE fails with "Access denied"
- Resolution: Use MySQL root user or admin user with GRANT privileges
- Impact: Blocks database setup
- Mitigation: Pre-migration checklist verifies permissions

**BLOCKER-6.2d: Data Corruption in SQLite Source**
- Symptom: dumpdata fails or JSON output is invalid
- Resolution: Backup corrupted SQLite, rollback to prior backup
- Impact: Blocks migration
- Mitigation: Unlikely (SQLite is stable); caught by dumpdata JSON validation

**BLOCKER-6.2e: Charset Mismatch Post-Load**
- Symptom: Text fields show garbled characters or emoji errors
- Resolution: Verify MySQL database charset=utf8mb4, reload data
- Impact: Data usability (not loss)
- Mitigation: Charset validated in design phase

---

## 7. ROLLBACK & CONTINGENCY PLAN

### 7.1 Rollback Trigger Conditions

**Rollback executed if ANY of the following occur:**

1. **MySQL Connection Fails**
   - Symptom: `python manage.py dbshell --database=mysql` times out or "Access denied"
   - Action: Delete MySQL database, restore SQLite backup

2. **Data Validation Fails**
   - Symptom: Row count mismatch, orphaned records, or integrity errors
   - Action: Delete MySQL database, restore SQLite backup, investigate JSON dump

3. **Application Fails on MySQL**
   - Symptom: `python manage.py runserver` crashes with database error
   - Action: Delete MySQL database, restore SQLite backup, debug settings

4. **Test Suite Fails**
   - Symptom: `python manage.py test --database=mysql` shows failures
   - Action: Delete MySQL database, investigate failure, restore SQLite backup

5. **Cascading Delete Doesn't Work**
   - Symptom: Parent record deleted but child records remain (orphaned)
   - Action: Delete MySQL database, restore SQLite backup, verify FK definitions

6. **Unique Constraint Fails**
   - Symptom: Duplicate insert succeeds or error message unclear
   - Action: Delete MySQL database, investigate MySQL configuration, restore SQLite

---

### 7.2 Rollback Process (Step-by-Step)

**Step 1: Stop Application**
```bash
# Stop Django runserver (Ctrl+C) and any other processes accessing MySQL
pkill -f "python manage.py"
```

**Step 2: Delete MySQL Database**
```bash
mysql -u root -p -e "DROP DATABASE IF EXISTS aficionados_network;"
```

**Step 3: Restore SQLite Backup**
```bash
cp db.sqlite3.backup db.sqlite3
```

**Step 4: Verify Backup Integrity**
```bash
md5sum -c db.sqlite3.md5  # Should print OK
```

**Step 5: Switch Environment to SQLite**
```bash
# Update .env
sed -i 's/DB_ENGINE=.*/DB_ENGINE=sqlite3/' .env

# OR manually edit .env:
# DB_ENGINE=sqlite3
# DB_NAME=db.sqlite3
```

**Step 6: Verify SQLite is Accessible**
```bash
python manage.py dbshell
# Should open SQLite prompt
```

**Step 7: Run Django Checks**
```bash
python manage.py check
# Should report OK
```

**Step 8: Start Application**
```bash
python manage.py runserver
# Should start without errors
```

**Step 9: Verify Data Integrity**
```bash
python manage.py shell
>>> from posts.models import Posts
>>> Posts.objects.count()
# Should match pre-migration count
```

**Total Rollback Time:** <2 minutes

---

### 7.3 Contingency Actions

**If Rollback Fails (Rare):**

1. **SQLite Backup File Missing**
   - Last resort: Check git history for db.sqlite3 snapshot
   - Or: Contact project maintainer for backup copy

2. **Backup File Corrupted (MD5 Mismatch)**
   - Check if time-machine backup exists (system backup)
   - Or: Accept data loss and recreate from export/source control

3. **MySQL Persists (Can't Delete)**
   - Manually verify MySQL stopped: `sudo systemctl stop mysql`
   - Then retry DROP DATABASE
   - Or: Rename database directory in MySQL data folder

---

### 7.4 Communication Plan

**If Rollback Triggers:**

- Document reason for rollback in `.sdd/changes/sqlite-to-mysql-migration/verify-report.md`
- List blockers that need resolution before retry
- Schedule follow-up investigation

**Example:**
```
ROLLBACK REASON: Data integrity validation failed
- Row count mismatch: SQLite 523 rows, MySQL 512 rows
- Missing: 11 rows in posts_posts
- Investigation: Check dumpdata JSON for export errors

NEXT STEPS:
- Investigate dumpdata JSON integrity
- Check for duplicate row keys in dump
- Verify no data was missed during export
```

---

## 8. ACCEPTANCE CRITERIA

### 8.1 Specification Phase Success

- [ ] All 10 validation scenarios (S1-S10) have YES/NO criteria
- [ ] Each scenario includes Gherkin GIVEN/WHEN/THEN format
- [ ] Each scenario has SQL queries or Python tests for verification
- [ ] Database setup requirements fully documented
- [ ] Environment variables documented with examples
- [ ] Driver options (mysqlclient vs PyMySQL) explained
- [ ] All assumptions and preconditions listed
- [ ] Rollback procedure is clear and <2 minute timeline
- [ ] All codebase examples are accurate (reference actual files/models)
- [ ] No ambiguity in success/failure criteria

### 8.2 Specification Quality Checklist

- [ ] Readable by non-technical stakeholders
- [ ] Precise enough for design phase (no vague language)
- [ ] Covers positive path (success) and negative path (failures)
- [ ] Covers edge cases (M2M, signals, cascading deletes)
- [ ] Covers rollback scenario
- [ ] All decisions justified with alternatives
- [ ] No conflicts or contradictions
- [ ] Validation checkpoints are verifiable (SQL/Python provided)

---

## 9. GLOSSARY

| Term | Definition |
|------|-----------|
| **dumpdata** | Django command to export data as JSON (database-agnostic) |
| **loaddata** | Django command to import JSON data into database |
| **M2M** | Many-to-Many relationship (through junction table) |
| **O2O** | One-to-One relationship |
| **FK** | Foreign Key constraint |
| **Cascading Delete** | ON DELETE CASCADE: child records auto-deleted when parent deleted |
| **Rollback** | Restore to pre-migration state (SQLite backup) |
| **Charset** | Character encoding (utf8mb4 = full Unicode) |
| **Collation** | Sort order and comparison rules for charset |
| **Integrity** | Data correctness (no corruption, no orphaned records) |
| **Dual-DB Config** | Settings.py supports multiple databases (SQLite + MySQL) |

---

## 10. REFERENCES & RESOURCES

- [Django Database Backend Configuration](https://docs.djangoproject.com/en/6.0/ref/settings/#databases)
- [Django Dumpdata/Loaddata](https://docs.djangoproject.com/en/6.0/ref/django-admin/#dumpdata)
- [mysqlclient Documentation](https://mysqlclient.readthedocs.io/)
- [PyMySQL Documentation](https://pymysql.readthedocs.io/)
- [MySQL Character Sets](https://dev.mysql.com/doc/refman/8.0/en/charset.html)
- Project repo: [aficionados_network/settings.py](aficionados_network/settings.py)

---

**SPECIFICATION COMPLETE**

**Next Phase:** Design (exact commands, scripts, validation queries)

**Previous Artifacts:** [Proposal](proposal.md) | [Exploration](explore.md)

---

*Document Version: 1.0*  
*Status: Ready for Design Phase*  
*Author: GitHub Copilot (SDD Specification Phase)*
