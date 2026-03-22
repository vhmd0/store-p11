"""
Seed the SQLite database from data_seeding.sql.

Handles MySQL-exported SQL by:
- Stripping MySQL-only statements (SET, START TRANSACTION, COMMIT,
  ROLLBACK, LOCK/UNLOCK TABLES, ALTER TABLE … AUTO_INCREMENT)
- Converting INSERT INTO → INSERT OR IGNORE INTO to skip duplicates
- Executing statement-by-statement with per-statement error reporting
"""

import re
import sqlite3
import sys
from pathlib import Path

SQL_FILE = Path("data_seeding.sql")
DB_FILE = Path("db.sqlite3")

if not SQL_FILE.exists():
    print(f"  ✘  {SQL_FILE} not found.", file=sys.stderr)
    sys.exit(1)

if not DB_FILE.exists():
    print(f"  ✘  {DB_FILE} not found — run migrations first.", file=sys.stderr)
    sys.exit(1)

sql = SQL_FILE.read_text(encoding="utf-8")

# ── 1. Strip MySQL-only statements ───────────────────────────────────────────
STRIP_PATTERNS = [
    r"(?im)^\s*SET\s+[^;]+;",                        # SET FOREIGN_KEY_CHECKS, SET SQL_MODE …
    r"(?im)^\s*START\s+TRANSACTION\s*;",              # START TRANSACTION
    r"(?im)^\s*COMMIT\s*;",                           # COMMIT
    r"(?im)^\s*ROLLBACK\s*;",                         # ROLLBACK
    r"(?im)^\s*LOCK\s+TABLES\s+[^;]+;",              # LOCK TABLES
    r"(?im)^\s*UNLOCK\s+TABLES\s*;",                 # UNLOCK TABLES
    r"(?im)^\s*ALTER\s+TABLE\s+\S+\s+AUTO_INCREMENT[^;]*;",  # AUTO_INCREMENT resets
]
for pattern in STRIP_PATTERNS:
    sql = re.sub(pattern, "", sql)

# ── 2. Convert INSERT INTO → INSERT OR IGNORE INTO (skip duplicates) ─────────
sql = re.sub(r"(?i)\bINSERT\s+INTO\b", "INSERT OR IGNORE INTO", sql)

# ── 3. Split into individual statements ──────────────────────────────────────
statements = [s.strip() for s in sql.split(";") if s.strip()]

# ── 4. Execute ───────────────────────────────────────────────────────────────
db = sqlite3.connect(DB_FILE)
db.execute("PRAGMA foreign_keys = OFF")  # mirrors SET FOREIGN_KEY_CHECKS=0

errors = 0
inserted = 0
try:
    with db:
        for stmt in statements:
            try:
                db.execute(stmt)
                inserted += 1
            except sqlite3.Error as e:
                print(f"  ⚠  Skipped: {e}", file=sys.stderr)
                errors += 1
finally:
    db.execute("PRAGMA foreign_keys = ON")
    db.close()

if errors:
    print(f"\n  ⚠  Seeding done — {inserted} ok, {errors} skipped.")
else:
    print(f"  ✔  All {inserted} statements executed successfully.")

sys.exit(0)
