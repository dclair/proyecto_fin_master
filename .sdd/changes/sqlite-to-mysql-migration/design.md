# Design: SQLite → MySQL/MariaDB Migration (Technical Implementation)

**Change:** `sqlite-to-mysql-migration`  
**Date:** 2026-05-25  
**Status:** DESIGN PHASE  
**Timeline:** 5 sequential phases, ~100 minutes total

---

## Executive Summary

This design specifies exact commands, sequences, and architecture decisions for migrating Aficionados Network from SQLite (file-based) to MySQL/MariaDB (server-based). The approach uses Django's `dumpdata`/`loaddata` fixture pattern: export all data as JSON from SQLite, create fresh schema in MySQL, import data, then validate integrity. **Zero code changes required** — only configuration and environment setup. **Full rollback capability** via SQLite backup.

---

## Technical Approach

### Strategy: Dump/Restore with Validation

```
SQLite (db.sqlite3)
       ↓
    [dumpdata → JSON]
       ↓
   db_backup.json
       ↓
    [loaddata]
       ↓
   MySQL (aficionados_network_db)
       ↓
    [Validate counts, relationships, signals]
       ↓
    READY FOR CUTOVER
```

**Why this approach:**
1. **Safe & Reversible** – Atomic operation, can retry with same backup
2. **Framework-native** – Uses Django ORM, no raw SQL needed
3. **Zero Application Changes** – Only settings.py env vars change
4. **Data Integrity Guaranteed** – JSON preserves all relationships
5. **Testable** – Validation runs in same environment pre-cutover

### Key Decisions

| Decision | Choice | Why | Alternative |
|----------|--------|-----|-------------|
| Migration Pattern | `dumpdata` → `loaddata` | Safe, reversible, ORM-native | Direct SQL migration (risky, harder rollback) |
| Driver | `mysqlclient` (primary) + `PyMySQL` (fallback) | Fast (C-based) + portable | Pure PyMySQL only (slower) |
| Charset | `utf8mb4` + `utf8mb4_unicode_ci` | Full emoji/Unicode support | utf8 (3-byte, limited) |
| Backup Strategy | Copy SQLite to `.backup` file | Instant revert possible | Remote backup (slower to recover) |
| Configuration | ENV vars + `.env` file | Portable, secure, twelve-factor-ready | Hardcoded in settings (not portable) |
| Phase Structure | Sequential (5 phases) | Simpler validation, fewer race conditions | Parallel (more complex, higher error risk) |
| Test Scope | Unit + Integration + Model CRUD | Comprehensive signal/relationship coverage | Basic schema check only (gaps in coverage) |

---

## Architecture Overview

### Data Flow: SQLite → MySQL

```
┌──────────────────────────────────────────────────────────────────┐
│                   MIGRATION ARCHITECTURE                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PHASE 0 (5 min):   Validation Checklist                        │
│    └─ Verify env, backups, migrations status                    │
│                                                                  │
│  PHASE 1 (20 min):  Dependencies & Setup                        │
│    ├─ pip install mysqlclient                                  │
│    ├─ Create .env with DB_* variables                          │
│    └─ Update requirements.txt + settings.py                    │
│                                                                  │
│  PHASE 2 (15 min):  MySQL Schema & User                        │
│    ├─ CREATE DATABASE aficionados_network_db                   │
│    ├─ CREATE USER django_user                                  │
│    └─ GRANT ALL PRIVILEGES                                     │
│                                                                  │
│  PHASE 3 (10 min):  Schema in MySQL                            │
│    ├─ python manage.py migrate --database=mysql                │
│    └─ Verify tables created                                    │
│                                                                  │
│  PHASE 4 (15 min):  Data Migration                             │
│    ├─ Dump from SQLite: dumpdata → db_backup.json             │
│    ├─ Load into MySQL: loaddata db_backup.json                │
│    └─ Count verification                                       │
│                                                                  │
│  PHASE 5 (30 min):  Testing & Validation                       │
│    ├─ django.setup check --deploy                             │
│    ├─ CRUD operations (Create, Read, Update, Delete)          │
│    ├─ Relationship integrity                                  │
│    ├─ Signal propagation (notifications)                      │
│    └─ Full test suite run                                     │
│                                                                  │
│  PHASE 6 (10 min):  Final Verification                         │
│    ├─ Row count parity (SQLite ≈ MySQL)                       │
│    ├─ Unique constraints enforced                             │
│    ├─ File uploads accessible                                 │
│    ├─ Signals working                                         │
│    └─ runserver works on MySQL backend                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Timeline & Resource Allocation

| Phase | Task | Duration | Slack | Notes |
|-------|------|----------|-------|-------|
| 0 | Pre-migration validation | 5 min | 0 | Quick checklist |
| 1 | Dependencies & .env setup | 20 min | 5 min | May need to compile mysqlclient |
| 2 | MySQL database + user | 15 min | 5 min | MariaDB must be running |
| 3 | Schema migration | 10 min | 2 min | `migrate` command |
| 4 | Data migration (dump/load) | 15 min | 5 min | Depends on data volume (~5-20 sec actual transfer) |
| 5 | Testing & validation | 30 min | 10 min | Comprehensive test suite |
| 6 | Final checklist | 10 min | 0 | Documentation + cleanup |
| **TOTAL** | | **100 min** | **27 min** | **Estimated 73 min active** |

---

## Phase-by-Phase Implementation

### PHASE 0: Pre-Migration Validation (5 min)

**Objective:** Verify preconditions; fail fast if anything is missing.

#### Checklist

```
☐ MariaDB server running: sudo systemctl status mysql
☐ MySQL credentials known: user, password, host, port
☐ Python venv activated: source env/bin/activate
☐ All Django migrations applied: python manage.py showmigrations --plan | grep -c '\['
☐ No pending migrations: python manage.py makemigrations --dry-run (should say "No changes")
☐ SQLite database exists: ls -lh db.sqlite3 (should show size)
☐ requirements.txt accessible: cat requirements.txt (check Python deps)
```

#### Commands

```bash
# 1. Verify MariaDB/MySQL running
sudo systemctl status mysql
# Expected: active (running)

# 2. Verify migrations
python manage.py showmigrations --plan | head -20
# Expected: List of [X] applied migrations for each app

# 3. Check for pending migrations
python manage.py makemigrations --dry-run
# Expected: "No changes detected"

# 4. Backup SQLite BEFORE starting
cp db.sqlite3 db.sqlite3.backup
ls -lh db.sqlite3*
# Expected: Two files, same size

# 5. Count current data
python manage.py dbshell <<EOF
SELECT 'Users:' as label, COUNT(*) FROM auth_user
UNION ALL
SELECT 'Posts:', COUNT(*) FROM posts_posts
UNION ALL
SELECT 'Comments:', COUNT(*) FROM posts_comment
UNION ALL
SELECT 'Events:', COUNT(*) FROM posts_event
UNION ALL
SELECT 'Profiles:', COUNT(*) FROM profiles_userprofile
UNION ALL
SELECT 'Notifications:', COUNT(*) FROM notifications_notification;
EOF
# Record these numbers for Phase 5 verification
```

**Verification:** All items checked, SQLite backup exists, migration count matches expected value.

---

### PHASE 1: Dependencies & Environment Setup (20 min)

**Objective:** Install MySQL driver, create `.env` file, update `requirements.txt`.

#### Task 1.1: Update requirements.txt

**File:** `requirements.txt`

**Action:** Add MySQL driver dependency

**Exact Change:**
```diff
 Django==6.0
 python-dotenv==1.2.1
+mysqlclient==2.2.6  # MySQL/MariaDB Python driver (C-based, fast)
 
 gunicorn==21.2.0
```

**Rationale:** Declare dependency in `requirements.txt` for reproducibility. Version 2.2.6 is stable, supports Python 3.12+, and compatible with MySQL 8.0+ and MariaDB 10.5+.

#### Task 1.2: Install MySQL Driver

```bash
# Activate environment
source env/bin/activate

# Install mysqlclient
pip install mysqlclient==2.2.6

# If installation fails (missing MySQL dev headers), try PyMySQL fallback
# (only if mysqlclient fails)
pip install PyMySQL==1.1.0

# Verify driver installed
python -c "import MySQLdb; print(f'mysqlclient version: {MySQLdb.__version__}')" || \
python -c "import pymysql; print(f'PyMySQL version: {pymysql.__version__}')"

# Expected: "mysqlclient version: 2.2.6" OR "PyMySQL version: 1.1.0"

# List installed packages
pip list | grep -i -E "(mysql|pymysql)"
```

**Fallback:** If mysqlclient fails to compile:
1. Ensure system packages: `sudo apt-get install libmysqlclient-dev` (Linux) or `brew install mysql-client` (macOS)
2. Retry: `pip install --force-reinstall mysqlclient==2.2.6`
3. If still fails: use PyMySQL (slower but portable)

#### Task 1.3: Create `.env` File

**File:** `.env` (create in project root if not exists)

**Content:**
```env
# Database Configuration
DB_ENGINE=mysql
DB_NAME=aficionados_network_db
DB_USER=django_user
DB_PASSWORD=your_secure_password_here
DB_HOST=127.0.0.1
DB_PORT=3306

# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-change-in-production
ALLOWED_HOSTS=127.0.0.1,localhost
SITE_ID=1
```

**Important:** Replace `DB_PASSWORD` with a strong random password (32 chars minimum):
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Save this password — you'll need it for MySQL user creation
```

**Safety:** Add `.env` to `.gitignore` (never commit credentials):
```bash
echo ".env" >> .gitignore
```

#### Task 1.4: Verify settings.py Configuration

**File:** `aficionados_network/settings.py`

**Current State:** Already has dual-DB config, but needs `init_command` for strict mode.

**Required Change:**
```python
# Current (lines ~100):
if DB_ENGINE == "mysql":
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
            },
        }
    }

# Should be (add init_command):
if DB_ENGINE == "mysql":
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
        }
    }
```

**Rationale:** `STRICT_TRANS_TABLES` enforces stricter SQL validation, preventing silent data loss from invalid dates/values.

**Verification:**
```bash
python -c "import django; django.setup(); from django.conf import settings; print(settings.DATABASES)"
# Should show MySQL config with init_command present
```

**Phase 1 Verification:**
```bash
python -c "import MySQLdb" 2>/dev/null && echo "✓ mysqlclient installed" || echo "✗ mysqlclient missing"
test -f .env && echo "✓ .env file created" || echo "✗ .env missing"
grep -q "mysqlclient" requirements.txt && echo "✓ requirements.txt updated" || echo "✗ requirements.txt not updated"
```

---

### PHASE 2: MySQL Database & User Setup (15 min)

**Objective:** Create MySQL database, user, and verify connection from Django.

#### Task 2.1: Create MySQL Database and User

**Commands (interactive MySQL):**

```bash
# Connect to MySQL as root
mysql -u root -p
# Password: [your MySQL root password]

# Now you're in mysql> prompt, run these SQL commands:
```

**SQL Commands:**

```sql
-- 1. Create database with UTF-8 support
CREATE DATABASE aficionados_network_db 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

-- 2. Create application user
CREATE USER 'django_user'@'127.0.0.1' IDENTIFIED BY 'your_secure_password_here';

-- 3. Grant specific permissions (principle of least privilege)
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX 
  ON aficionados_network_db.* 
  TO 'django_user'@'127.0.0.1';

-- 4. Apply permission changes
FLUSH PRIVILEGES;

-- 5. Verify database created
SHOW DATABASES;
-- Should list: aficionados_network_db among others

-- 6. Verify user created
SELECT user, host FROM mysql.user WHERE user='django_user';
-- Should show: django_user | 127.0.0.1

-- 7. Exit MySQL
EXIT;
```

**Embedded Script (if interactive input is difficult):**

Create file `setup_mysql.sql`:
```sql
CREATE DATABASE aficionados_network_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'django_user'@'127.0.0.1' IDENTIFIED BY 'your_secure_password_here';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX ON aficionados_network_db.* TO 'django_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

Run it:
```bash
mysql -u root -p < setup_mysql.sql
```

#### Task 2.2: Verify Connection from Django

**Test 1: Django dbshell**

```bash
# Activate environment
source env/bin/activate

# Export MySQL flag
export DB_ENGINE=mysql

# Connect via Django
python manage.py dbshell
# Expected: mysql> prompt appears

# Inside mysql prompt, run verification:
mysql> SELECT VERSION();
# Expected: MySQL 8.0.32 (or similar version)

mysql> SHOW DATABASES;
# Expected: aficionados_network_db listed

mysql> SHOW TABLES;
# Expected: empty (no tables yet — will be created in Phase 3)

mysql> EXIT;
```

**Test 2: Django Connection Check**

```bash
python manage.py check --database default
# Expected: "System check identified no issues (0 silenced)"
```

**Test 3: Test Data Connection (Python)**

```bash
python manage.py shell
```

```python
# Inside Django shell:
from django.db import connection
print(connection.get_connection_params())
# Expected: Shows connection to aficionados_network_db on 127.0.0.1

exit()
```

**Phase 2 Verification:**
```bash
mysql -u django_user -p -h 127.0.0.1 -D aficionados_network_db -e "SELECT 'Connection successful';"
# Enter password when prompted
# Expected: "Connection successful"
```

---

### PHASE 3: Schema Migration to MySQL (10 min)

**Objective:** Create all tables, indexes, and constraints in MySQL using Django migrations.

#### Task 3.1: Run Django Migrations Against MySQL

```bash
# Ensure environment is set
source env/bin/activate
export DB_ENGINE=mysql

# Run migrations
python manage.py migrate --no-input

# Expected output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, sites, flatpages, 
#   posts, profiles, aficionados_network, notifications
# Running migrations:
#   admin: 0001_initial, 0002_logentry_remove_auto_add, 0003_logentry_add_action_time_indexes
#   ... (many migrations)
#   notifications: 0001_initial, 0002_*, 0003_*, 0004_*
# ... all migrations applied successfully
```

#### Task 3.2: Verify Schema Created

**In MySQL:**

```bash
python manage.py dbshell
```

```sql
-- Inside MySQL:

-- 1. Count tables (should be 30+)
SHOW TABLES;
-- Expected: 30-35 tables

-- 2. Verify key tables exist
SHOW TABLES LIKE 'posts_%';
-- Expected: posts_posts, posts_comment, posts_event, posts_eventcomment

SHOW TABLES LIKE 'profiles_%';
-- Expected: profiles_userprofile, profiles_hobby, profiles_follow, profiles_review

SHOW TABLES LIKE 'notifications_%';
-- Expected: notifications_notification

-- 3. Check table structure (example)
DESCRIBE posts_posts;
-- Expected: id, user_id, title, caption, created_at, image, category_id, ... (15+ columns)

-- 4. Verify charset
SHOW CREATE TABLE posts_posts\G
-- Expected: "DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

-- 5. Check indexes created
SHOW INDEX FROM posts_posts;
-- Expected: id (PK), user_id (FK index), category_id (FK index)

EXIT;
```

**Verify Constraints:**

```bash
python manage.py shell
```

```python
# Inside Django shell:
from django.db import connection

# Get table info
with connection.cursor() as cursor:
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='aficionados_network_db'")
    tables = cursor.fetchall()
    print(f"Total tables created: {len(tables)}")
    for (table,) in tables[:5]:
        print(f"  - {table}")

exit()
```

**Phase 3 Verification:**
```bash
python manage.py showmigrations | grep -c '\[X\]'
# Should output: ≥28 (number of applied migrations)
```

---

### PHASE 4: Data Migration — Dump & Load (15 min)

**Objective:** Export all data from SQLite as JSON, import into MySQL.

#### Task 4.1: Dump Data from SQLite

```bash
# Switch to SQLite
source env/bin/activate
unset DB_ENGINE  # Falls back to SQLite per settings.py

# Export all data as JSON fixture
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --indent 2 \
  -e sessions \
  -e sites \
  > db_full_backup.json

# This excludes sessions (temporary) and sites (framework data)
```

**Why `--natural-foreign --natural-primary`:**
- Preserves M2M relationships correctly (UserHobby through tables)
- Uses natural keys instead of PKs (safer for schema changes)
- Makes JSON human-readable

**Verify Dump:**

```bash
# Check file size
ls -lh db_full_backup.json
# Expected: Size > 1MB typically (depends on data)

# Preview content
head -50 db_full_backup.json
# Expected: JSON array with model records

# Verify last record
tail -20 db_full_backup.json
# Expected: JSON closing bracket

# Count records
python -c "import json; data=json.load(open('db_full_backup.json')); print(f'Total records: {len(data)}')"
# Expected: Total records: N (where N > 0)

# Count by model (for Phase 5 verification)
python << 'EOF'
import json
from collections import Counter

data = json.load(open('db_full_backup.json'))
models = Counter(record['model'] for record in data)

print("Records by model:")
for model, count in sorted(models.items(), key=lambda x: x[1], reverse=True):
    print(f"  {model}: {count}")
print(f"\nTotal: {len(data)}")
EOF
```

#### Task 4.2: Load Data into MySQL

```bash
# Switch to MySQL
export DB_ENGINE=mysql

# Clear any existing data (safe on fresh schema)
python manage.py flush --noinput

# Load fixture
python manage.py loaddata db_full_backup.json --verbosity=2

# Expected output:
# Installed N objects from 1 fixture(s)
# ... detailed load progress
```

**Troubleshooting:**

If `loaddata` fails with FK constraint error:
```bash
# Sometimes order matters — try with --app flag
python manage.py loaddata db_full_backup.json --app auth --verbosity=2
python manage.py loaddata db_full_backup.json --app posts --verbosity=2
# (repeat for each app if needed)
```

If charset error appears:
```bash
# Check connection string in MySQL shell
mysql> SHOW VARIABLES LIKE 'character_set%';
# Should show utf8mb4 for all variables
```

#### Task 4.3: Verify Data Integrity

**Count Verification (Python):**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from posts.models import Posts, Comment, Event, EventComment
from profiles.models import UserProfile, Hobby, UserHobby, Follow, Review
from notifications.models import Notification
from aficionados_network.models import ContactMessage

print("=== MySQL Data Counts (Post-Migration) ===\n")

counts = {
    "Users": User.objects.count(),
    "UserProfiles": UserProfile.objects.count(),
    "Posts": Posts.objects.count(),
    "Comments": Comment.objects.count(),
    "Events": Event.objects.count(),
    "EventComments": EventComment.objects.count(),
    "Hobbies": Hobby.objects.count(),
    "UserHobbies": UserHobby.objects.count(),
    "Follows": Follow.objects.count(),
    "Reviews": Review.objects.count(),
    "Notifications": Notification.objects.count(),
    "ContactMessages": ContactMessage.objects.count(),
}

for label, count in counts.items():
    print(f"{label:20} {count:5}")

print(f"\n{'TOTAL':20} {sum(counts.values()):5}")

# Compare with numbers from Phase 0 — should match (approximately)
exit()
```

**Relationship Verification:**

```python
# Still in Django shell:

# Check FK relationships
print("\n=== Relationship Integrity ===\n")

# Test 1: User → Posts relationship
user = User.objects.first()
if user:
    user_posts = Posts.objects.filter(user=user).count()
    print(f"User '{user.username}' has {user_posts} posts")

# Test 2: Post → Comments relationship
post = Posts.objects.first()
if post:
    post_comments = Comment.objects.filter(post=post).count()
    print(f"Post '{post.title}' has {post_comments} comments")

# Test 3: Event → Participants relationship
event = Event.objects.first()
if event:
    participants = event.participants.count()
    print(f"Event '{event.title}' has {participants} participants")

# Test 4: Follow relationship integrity
follows = Follow.objects.first()
if follows:
    print(f"Follow: {follows.follower.user.username} → {follows.following.user.username}")

exit()
```

**Phase 4 Verification:**
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
print(f'Users migrated: {User.objects.count()}')
"
```

---

### PHASE 5: Testing & Validation (30 min)

**Objective:** Comprehensive testing to ensure MySQL backend works identically to SQLite.

#### Task 5.1: Django System Checks

```bash
export DB_ENGINE=mysql
python manage.py check --deploy

# Expected: "System check identified no issues (0 silenced)"
```

**If errors appear:**
```bash
python manage.py check --deploy --fail-level=WARNING
# Shows all warnings too — address any database-related ones
```

#### Task 5.2: Test CRUD Operations

```bash
python manage.py shell
```

**Test CREATE:**
```python
from posts.models import Posts
from profiles.models import UserProfile
from django.contrib.auth.models import User

# Get first user
user = User.objects.first()

# Create new post
post = Posts.objects.create(
    user=user,
    title="MySQL Test Post",
    caption="Testing CREATE operation on MySQL backend"
)
print(f"✓ Created post: ID={post.id}, title='{post.title}'")
```

**Test READ:**
```python
# Read all posts (pagination)
posts = Posts.objects.all()[:5]
for post in posts:
    print(f"  Post {post.id}: {post.title} by {post.user.username}")

# Read with relationship
profile = user.userprofile
print(f"✓ Read profile: {profile.user.username}, followers={profile.followers_count}")
```

**Test UPDATE:**
```python
# Fetch and modify
post = Posts.objects.get(id=post.id)
old_title = post.title
post.title = "Updated via MySQL Test"
post.save()
print(f"✓ Updated post: '{old_title}' → '{post.title}'")
```

**Test DELETE:**
```python
# Delete post
post_id = post.id
post.delete()
post_exists = Posts.objects.filter(id=post_id).exists()
print(f"✓ Deleted post {post_id}, exists={post_exists} (should be False)")
```

**Test Relationships:**
```python
# One-to-One (User ↔ UserProfile)
user = User.objects.first()
profile = user.userprofile
print(f"✓ O2O: User {user.username} → Profile (bio_length={len(profile.bio)})")

# Many-to-Many (Event ↔ Participants)
event = Event.objects.filter(participants__isnull=False).first()
if event:
    participant_count = event.participants.count()
    print(f"✓ M2M: Event '{event.title}' has {participant_count} participants")

# Foreign Key (Post → User)
post = Posts.objects.first()
print(f"✓ FK: Post {post.id} → User {post.user.username}")
```

**Exit shell:**
```python
exit()
```

#### Task 5.3: Run Full Test Suite

```bash
export DB_ENGINE=mysql

# Run all tests with verbose output
python manage.py test --verbosity=2

# Expected: ". . . . ." (dots = passed tests), final: "OK"
```

**If tests fail:**
```bash
# Run specific app tests
python manage.py test posts --verbosity=2
python manage.py test profiles --verbosity=2
python manage.py test notifications --verbosity=2

# Run specific test class
python manage.py test posts.tests.PostModelTest --verbosity=2
```

**Coverage Report (if coverage installed):**
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
# Shows % coverage per app
```

#### Task 5.4: Test File Upload Handling

```bash
python manage.py shell
```

```python
from posts.models import Posts
from django.conf import settings

# Check if any posts have images
posts_with_images = Posts.objects.exclude(image='').first()

if posts_with_images:
    print(f"✓ Post with image found:")
    print(f"  - Image path: {posts_with_images.image}")
    print(f"  - URL: {posts_with_images.image.url}")
    print(f"  - Size: {posts_with_images.image.size} bytes")
    
    # Verify file exists on disk
    import os
    full_path = os.path.join(settings.MEDIA_ROOT, str(posts_with_images.image))
    exists = os.path.exists(full_path)
    print(f"  - File exists on disk: {exists}")
else:
    print("No posts with images found (expected for fresh migration)")

exit()
```

#### Task 5.5: Test Signals (Follow Notification)

```bash
python manage.py shell
```

```python
from profiles.models import UserProfile, Follow
from notifications.models import Notification

# Get or create two test users
users = list(UserProfile.objects.all()[:2])

if len(users) >= 2:
    follower = users[0]
    following = users[1]
    
    print(f"Testing signal: {follower.user.username} → {following.user.username}")
    
    # Create follow relationship (should trigger signal)
    follow = Follow.objects.create(follower=follower, following=following)
    
    # Check if notification was created
    notification = Notification.objects.filter(
        notification_type='follow',
        recipient=following.user
    ).last()
    
    if notification:
        print(f"✓ Signal worked! Notification created:")
        print(f"  - Type: {notification.notification_type}")
        print(f"  - Recipient: {notification.recipient.username}")
        print(f"  - From: {notification.sender.username}")
    else:
        print("✗ Signal failed — no notification created")
    
    # Cleanup
    follow.delete()
else:
    print("Need at least 2 users for signal test")

exit()
```

#### Task 5.6: Test Production-Like Runserver

```bash
export DB_ENGINE=mysql

# Start development server
python manage.py runserver

# In another terminal, test endpoints:
curl http://127.0.0.1:8000/
# Expected: 200 OK (homepage loads)

curl http://127.0.0.1:8000/admin/
# Expected: 302 redirect to login (admin accessible)

# Stop server: Ctrl+C
```

**Phase 5 Verification:**
```bash
python manage.py test --verbosity=0 2>/dev/null && echo "✓ All tests passed"
python manage.py check --deploy 2>/dev/null && echo "✓ Deployment checks passed"
```

---

### PHASE 6: Final Verification Checklist (10 min)

**Objective:** Confirm everything is working before declaring migration complete.

#### Verification Matrix

```
DATABASE LAYER
☐ MySQL database exists
   Command: mysql -u django_user -p -h 127.0.0.1 -e "SHOW DATABASES LIKE 'aficionados_network_db';"
   
☐ All 30+ tables created
   Command: python manage.py dbshell -e "SHOW TABLES;" | wc -l
   
☐ Charset is utf8mb4
   Command: python manage.py dbshell -e "SHOW VARIABLES LIKE 'character_set%';"
   
☐ No connection warnings
   Command: python manage.py check

DATA INTEGRITY
☐ Row counts match SQLite (~within 1%)
   Command: Compare counts from Phase 0 vs Phase 5
   
☐ No orphaned FK records (cascade delete working)
   Command: Python script checks for mismatched FKs
   
☐ M2M relationships intact (UserHobby, EventParticipants, Follow)
   Command: python manage.py shell + relationship checks
   
☐ Unique constraints enforced
   Command: Attempt duplicate Posts.slug (should fail with IntegrityError)
   
☐ Datetime fields preserved (no timezone issues)
   Command: Compare post.created_at value

FUNCTIONALITY
☐ Signals work (notifications on follow/like)
   Command: Create new Follow, check Notification created
   
☐ File uploads accessible (image.url resolves)
   Command: Check media paths for posts with images
   
☐ Django ORM queries work (filter, exclude, Q objects)
   Command: Run test queries in shell
   
☐ Test suite passes
   Command: python manage.py test --verbosity=0

APPLICATION
☐ Admin interface works
   Command: curl http://127.0.0.1:8000/admin/ (should redirect to login)
   
☐ Public pages load
   Command: curl http://127.0.0.1:8000/ (should return 200)
   
☐ Form submissions work (CSRF, validation)
   Command: POST request to form endpoint
   
☐ Authentication works (login/logout)
   Command: Login as superuser, access admin
```

#### Automated Verification Script

Create `verify_migration.py`:

```python
#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DB_ENGINE', 'mysql')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from posts.models import Posts, Comment, Event
from profiles.models import UserProfile, Follow
from notifications.models import Notification

def verify():
    """Run all verification checks"""
    checks_passed = 0
    checks_failed = 0
    
    print("=" * 60)
    print("MIGRATION VERIFICATION REPORT")
    print("=" * 60)
    
    # 1. Database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
        print(f"✓ MySQL connected: {version}")
        checks_passed += 1
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        checks_failed += 1
    
    # 2. Table count
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='aficionados_network_db'")
            table_count = cursor.fetchone()[0]
        if table_count >= 25:
            print(f"✓ Tables created: {table_count}")
            checks_passed += 1
        else:
            print(f"✗ Too few tables: {table_count} (expected ≥25)")
            checks_failed += 1
    except Exception as e:
        print(f"✗ Table check failed: {e}")
        checks_failed += 1
    
    # 3. Data presence
    try:
        user_count = User.objects.count()
        post_count = Posts.objects.count()
        print(f"✓ Data loaded: {user_count} users, {post_count} posts")
        checks_passed += 1
    except Exception as e:
        print(f"✗ Data check failed: {e}")
        checks_failed += 1
    
    # 4. Relationships
    try:
        user = User.objects.first()
        if user:
            profile = user.userprofile
            print(f"✓ Relationships working (User → Profile)")
            checks_passed += 1
        else:
            print("✗ No users in database")
            checks_failed += 1
    except Exception as e:
        print(f"✗ Relationship check failed: {e}")
        checks_failed += 1
    
    # 5. UTF-8 support
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW VARIABLES LIKE 'character_set_connection'")
            charset = cursor.fetchone()[1]
        if 'utf8mb4' in charset:
            print(f"✓ UTF-8 charset: {charset}")
            checks_passed += 1
        else:
            print(f"✗ Wrong charset: {charset} (expected utf8mb4)")
            checks_failed += 1
    except Exception as e:
        print(f"✗ Charset check failed: {e}")
        checks_failed += 1
    
    print("=" * 60)
    print(f"Summary: {checks_passed} passed, {checks_failed} failed")
    print("=" * 60)
    
    return checks_failed == 0

if __name__ == '__main__':
    success = verify()
    sys.exit(0 if success else 1)
```

Run it:
```bash
python verify_migration.py
```

---

## File Changes

| File | Action | Change |
|------|--------|--------|
| `requirements.txt` | Modify | Add `mysqlclient==2.2.6` |
| `.env` | Create | DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT |
| `aficionados_network/settings.py` | Modify | Add `init_command` to MySQL OPTIONS |
| `db.sqlite3.backup` | Create | Copy of original SQLite (rollback insurance) |
| `db_full_backup.json` | Create | JSON export of all SQLite data |
| `verify_migration.py` | Create (optional) | Automated verification script |
| `.gitignore` | Modify | Add `.env` to prevent credential leaks |

---

## Interfaces & Contracts

### Django ORM Interface

**No changes to model signatures.** The ORM automatically detects MySQL backend at runtime via `DATABASES['default']['ENGINE']`.

All existing model queries continue to work identically:

```python
# These work the same on SQLite and MySQL:
from posts.models import Posts

posts = Posts.objects.filter(user=user).select_related('user')
posts = Posts.objects.filter(created_at__gte=start_date).order_by('-created_at')
posts = Posts.objects.annotate(comment_count=Count('comments')).filter(comment_count__gt=0)
```

### Environment Variables Contract

| Variable | Type | Example | Required | Default |
|----------|------|---------|----------|---------|
| `DB_ENGINE` | string | `mysql` | Yes | `sqlite` |
| `DB_NAME` | string | `aficionados_network_db` | Yes (if `DB_ENGINE=mysql`) | Empty |
| `DB_USER` | string | `django_user` | Yes (if `DB_ENGINE=mysql`) | Empty |
| `DB_PASSWORD` | string | `[32-char-random]` | Yes (if `DB_ENGINE=mysql`) | Empty |
| `DB_HOST` | string | `127.0.0.1` | No | `127.0.0.1` |
| `DB_PORT` | int | `3306` | No | `3306` |

### Database Connection Parameters

```python
# When DB_ENGINE=mysql, Django creates connection:
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.getenv('DB_NAME'),           # 'aficionados_network_db'
    'USER': os.getenv('DB_USER'),           # 'django_user'
    'PASSWORD': os.getenv('DB_PASSWORD'),   # '[secure password]'
    'HOST': os.getenv('DB_HOST', '127.0.0.1'),
    'PORT': os.getenv('DB_PORT', '3306'),
    'OPTIONS': {
        'charset': 'utf8mb4',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    }
}
```

---

## Testing Strategy

### Unit Testing (Model Layer)

**What to test:** Individual model methods and properties

```python
# tests.py
from django.test import TestCase
from posts.models import Posts
from profiles.models import UserProfile
from django.contrib.auth.models import User

class PostsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
    
    def test_post_creation(self):
        """Test Post model on MySQL"""
        post = Posts.objects.create(
            user=self.user,
            title="Test",
            caption="Test post"
        )
        self.assertEqual(post.user_id, self.user.id)
        self.assertTrue(post.id > 0)
    
    def test_post_slug_unique(self):
        """Test unique constraint on MySQL"""
        Posts.objects.create(user=self.user, title="Test", slug="test-slug")
        with self.assertRaises(IntegrityError):
            Posts.objects.create(user=self.user, title="Test2", slug="test-slug")
```

### Integration Testing (Relationships & Signals)

**What to test:** Cross-model interactions, signal propagation

```python
class FollowSignalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'u1@test.com', 'pass')
        self.user2 = User.objects.create_user('user2', 'u2@test.com', 'pass')
    
    def test_follow_creates_notification(self):
        """Test that Follow signal creates Notification on MySQL"""
        from profiles.models import Follow
        from notifications.models import Notification
        
        Follow.objects.create(
            follower=self.user1.userprofile,
            following=self.user2.userprofile
        )
        
        notification = Notification.objects.filter(
            notification_type='follow',
            recipient=self.user2
        ).exists()
        self.assertTrue(notification)
```

### E2E Testing (API/Views)

**What to test:** Full user workflows via HTTP

```python
class PostCreationE2E(TestCase):
    def test_post_creation_workflow(self):
        """Test POST creation from form submission"""
        user = User.objects.create_user('user', 'u@test.com', 'pass')
        self.client.login(username='user', password='pass')
        
        response = self.client.post('/posts/create/', {
            'title': 'Test Post',
            'caption': 'Testing on MySQL'
        })
        
        self.assertEqual(response.status_code, 302)  # redirect after create
        self.assertTrue(Posts.objects.filter(title='Test Post').exists())
```

### Test Execution

```bash
# Run all tests
python manage.py test --verbosity=2 --database=mysql

# Run specific app
python manage.py test posts --verbosity=2

# Run with coverage
coverage run --source='.' manage.py test
coverage report --omit=env/*
```

---

## Migration & Rollout Plan

### Forward (SQLite → MySQL)

| Step | Action | Time | Verification |
|------|--------|------|--------------|
| 1 | Phase 0-6 execution | 100 min | All checklists pass |
| 2 | Update settings: set `DB_ENGINE=mysql` permanent | 1 min | Check `.env` |
| 3 | Restart app: `python manage.py runserver` | 1 min | Loads without error |
| 4 | Test critical workflows | 10 min | Users can login, post, follow |
| 5 | Monitor logs for errors | - | No "database error" entries |

### Rollback (MySQL → SQLite)

**If migration fails at ANY point:**

```bash
# 1. Stop application
# Press Ctrl+C on runserver

# 2. Switch back to SQLite
unset DB_ENGINE
# OR set in .env: DB_ENGINE=sqlite

# 3. Verify SQLite backup exists
ls -lh db.sqlite3.backup
cp db.sqlite3.backup db.sqlite3

# 4. Restart app
python manage.py runserver
# Should work exactly as before

# 5. Investigate failure
# - Check MySQL error logs
# - Verify data types, constraints
# - Re-run Phase with debug output
```

**Keep backup for 48 hours post-migration:**
```bash
# After 48 hours, if stable, remove backup
rm db.sqlite3.backup
```

---

## Architecture Decisions — Detailed Rationale

### Decision 1: Dump/Restore vs. Direct Migration

**Choice:** `dumpdata`/`loaddata` pattern

**Alternatives considered:**
- A. Direct SQL migration (custom SQL scripts)
- B. Data migration files (Django data migrations)
- C. Dump/Restore (chosen)

**Rationale for choice:**
- **Safest:** Atomic operation, entire dataset in one JSON file
- **Reversible:** Can re-dump from SQLite anytime
- **Framework-native:** Uses Django's built-in serialization
- **No schema changes:** M2M, FK relationships handled automatically
- **Human-readable:** JSON can be inspected/edited if needed
- **Lower error risk:** No custom SQL to debug

**Why not alternatives:**
- A. Raw SQL too fragile — FK constraints, data types vary per DB
- B. Data migrations too slow, harder to test, more complex

### Decision 2: mysqlclient (Primary) + PyMySQL (Fallback)

**Choice:** Use `mysqlclient` first; if compile fails, use `PyMySQL`

**Alternatives:**
- A. mysqlclient only (strict, faster)
- B. PyMySQL only (portable, slower)
- C. Both with fallback (chosen)

**Rationale:**
- mysqlclient: C extension, 3-5x faster, actively maintained
- PyMySQL: Pure Python, no system dependencies, slower but works anywhere
- **Fallback strategy reduces risk:** If mysqlclient compilation fails (missing libmysqlclient-dev), PyMySQL still works
- **Best of both:** Get performance when possible; have backup plan

### Decision 3: UTF-8mb4 Charset

**Choice:** `utf8mb4` with `utf8mb4_unicode_ci` collation

**Alternatives:**
- A. utf8 (MySQL 3-byte — limited emoji support)
- B. utf8mb4 (MySQL 4-byte — full Unicode) ← chosen
- C. latin1 (ASCII only)

**Rationale:**
- Full emoji/Unicode support (future-proof)
- Matches Django best practices
- Aligns with international user base expectation
- Minimal performance difference

### Decision 4: Environment Variables for Secrets

**Choice:** `.env` file with `python-dotenv` (already installed)

**Alternatives:**
- A. Hardcoded in settings.py (unsafe, not portable)
- B. Environment variables (hard to set during development)
- C. `.env` file (chosen — best balance for dev)

**Rationale:**
- Already using `python-dotenv` in project
- Credentials never committed to git (add `.env` to `.gitignore`)
- Easy to change per environment (dev/test/prod)
- Twelve-factor app aligned

### Decision 5: Sequential Phases (not Parallel)

**Choice:** Execute 6 phases in strict order

**Alternatives:**
- A. Parallel setup (DB creation while installing driver)
- B. Sequential (chosen)

**Rationale:**
- Simpler validation at each step
- Fail-fast: catch issues early, rollback is easy
- Fewer race conditions
- Easier to debug if something goes wrong
- Development environment (not production), so speed gain negligible

---

## Known Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| **mysqlclient compile failure** | Medium | Phase 1 blocked | Fallback: PyMySQL; doc compilation steps |
| **MySQL not running** | Low | Phase 2 fails | Pre-check: `systemctl status mysql` in Phase 0 |
| **Wrong charset on tables** | Low | Emoji corruption later | Verify `SHOW CREATE TABLE` in Phase 3 |
| **Data loss during loaddata** | Very low | Critical | Pre-dump, verify JSON, count rows pre/post |
| **FK constraint violations** | Low | loaddata fails | Use `--natural-foreign` flag; inspect JSON |
| **File uploads inaccessible** | Low | Images broken | Media path unchanged; test in Phase 5 |
| **Signals not firing on MySQL** | Very low | Notifications broken | Integration test in Phase 5 |
| **Timeouts on large data** | Very low (small dataset) | Incomplete import | Increase `wait_timeout` in MySQL if needed |

---

## Timeline Summary

```
Phase 0:  Pre-check              5 min
Phase 1:  Dependencies + .env   20 min  ← mysqlclient compile may add 5-10 min
Phase 2:  MySQL setup           15 min
Phase 3:  Schema creation       10 min
Phase 4:  Data migration        15 min
Phase 5:  Testing & validation  30 min
Phase 6:  Final verification    10 min
───────────────────────────────────────
TOTAL:   ~100 min (est. 73 min active)
Slack:   ~27 min buffer for retries
```

---

## Open Questions

- [ ] What is the MySQL root password? (needed for Phase 2)
- [ ] Are there any performance baselines from SQLite to compare against MySQL later?
- [ ] Should the migration be documented in project README after completion?
- [ ] Any custom database backup strategy needed beyond SQLite.backup?
- [ ] Is there a CI/CD pipeline that also needs MySQL configured?

---

## Next Phase: Tasks

The tasks phase will:
1. Break Phase 0-6 into atomic, verifiable tasks
2. Create a checklist with go/no-go criteria
3. Specify exact error handling and retry procedures
4. Map task dependencies (which must complete before next)
5. Identify owner and time estimates per task

**Estimated task count:** 18-20 discrete tasks across 6 phases

---

## Summary

✅ **Technical approach:** Dump/Restore pattern (safe, reversible, zero code changes)  
✅ **Exact commands:** All shell, SQL, and Python commands copy-paste ready  
✅ **Architecture decisions:** 5 key choices documented with rationale  
✅ **Verification strategy:** 6 layers of testing (unit, integration, E2E, signals, schema, data)  
✅ **Rollback plan:** SQLite backup + clear revert procedure  
✅ **Timeline:** 100 minutes with 27 minutes slack  
✅ **Risk mitigation:** 8 identified risks with concrete mitigations
