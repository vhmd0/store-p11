#!/usr/bin/env python3
"""
Convert data_seeding.sql to Django JSON fixture files.

Usage:
    python3 convert_sql_to_fixtures.py

Output:
    fixtures/<table>.json  — one file per table
"""

import json
import re
from pathlib import Path

SQL_FILE = Path(__file__).resolve().parent / "data_seeding.sql"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Table name → Django "app.Model" mapping
TABLE_TO_MODEL = {
    "auth_user": "auth.User",
    "users_profile": "users.Profile",
    "users_address": "users.Address",
    "products_category": "products.Category",
    "products_brand": "products.Brand",
    "products_tag": "products.Tag",
    "products_product": "products.Product",
    "products_product_tags": "products.Product_tags",
    "products_review": "products.Review",
    "products_wishlist": "products.Wishlist",
    "orders_order": "orders.Order",
    "orders_orderitem": "orders.OrderItem",
    "cart_cart": "cart.Cart",
    "cart_cartitem": "cart.CartItem",
}

# Known boolean fields
BOOLEAN_FIELDS = {"is_superuser", "is_staff", "is_active", "is_default"}

# Known decimal fields
DECIMAL_FIELDS = {"price", "total_amount"}


def strip_sql_noise(sql: str) -> str:
    """Remove MySQL-only statements."""
    patterns = [
        r"(?im)^\s*SET\s+[^;]+;",
        r"(?im)^\s*START\s+TRANSACTION\s*;",
        r"(?im)^\s*COMMIT\s*;",
        r"(?im)^\s*ROLLBACK\s*;",
        r"(?im)^\s*LOCK\s+TABLES\s+[^;]+;",
        r"(?im)^\s*UNLOCK\s+TABLES\s*;",
        r"(?im)^\s*ALTER\s+TABLE\s+\S+\s+AUTO_INCREMENT[^;]*;",
        r"(?im)^\s*--.*?$",  # SQL comments
    ]
    for p in patterns:
        sql = re.sub(p, "", sql)
    return sql


def parse_value_string(raw: str) -> list:
    """Parse a single SQL value tuple like (1, 'hello', NULL, 42)."""
    values = []
    i = 0
    raw = raw.strip().strip("()")
    n = len(raw)

    while i < n:
        # Skip whitespace and commas
        while i < n and raw[i] in " \t\n\r,":
            i += 1
        if i >= n:
            break

        if raw[i] in ("'", '"'):
            # Quoted string
            quote = raw[i]
            i += 1
            buf = []
            while i < n:
                if raw[i] == quote:
                    # Escaped quote: ''
                    if i + 1 < n and raw[i + 1] == quote:
                        buf.append(quote)
                        i += 2
                        continue
                    i += 1
                    break
                buf.append(raw[i])
                i += 1
            values.append("".join(buf))
        elif raw[i : i + 4].upper() == "NULL":
            values.append(None)
            i += 4
        else:
            # Number
            start = i
            while i < n and raw[i] not in ",)":
                i += 1
            val = raw[start:i].strip()
            try:
                values.append(int(val))
            except ValueError:
                try:
                    values.append(float(val))
                except ValueError:
                    values.append(val)

    return values


def parse_sql(sql_text: str) -> list[dict]:
    """Parse all INSERT INTO statements."""
    # First strip noise
    sql_text = strip_sql_noise(sql_text)

    results = []

    # Find each INSERT block: INSERT INTO table (cols) VALUES (...), (...), (...);
    # We split on INSERT INTO boundaries
    parts = re.split(r"(?i)(?=INSERT\s+INTO)", sql_text)

    for part in parts:
        part = part.strip()
        if not part.upper().startswith("INSERT INTO"):
            continue

        # Extract table name
        m = re.match(r"(?i)INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)", part)
        if not m:
            continue

        table = m.group(1).strip().lower()
        columns = [c.strip().strip('"').strip("`") for c in m.group(2).split(",")]

        # Extract everything after VALUES keyword
        vals_match = re.search(r"(?i)\bVALUES\s*", part)
        if not vals_match:
            continue

        raw_values = part[vals_match.end() :]

        # Remove trailing semicolon and whitespace
        raw_values = raw_values.rstrip().rstrip(";").strip()

        # Find all tuples: (...)
        # Use a state machine to match parentheses correctly
        tuples = []
        depth = 0
        start = -1
        in_str = False
        str_char = None

        for i, ch in enumerate(raw_values):
            if in_str:
                if ch == str_char:
                    in_str = False
                continue

            if ch in ("'", '"'):
                in_str = True
                str_char = ch
                continue

            if ch == "(":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and start >= 0:
                    tuples.append(raw_values[start : i + 1])
                    start = -1

        rows = [parse_value_string(t) for t in tuples]

        results.append(
            {
                "table": table,
                "columns": columns,
                "rows": rows,
            }
        )

    return results


def to_django_fixture(parsed: list[dict]) -> dict[str, list[dict]]:
    """Convert parsed data to Django fixture records grouped by table."""
    fixtures = {}

    for entry in parsed:
        table = entry["table"]
        model = TABLE_TO_MODEL.get(table)
        if not model:
            print(f"  ⚠  Skipping unknown table: {table}")
            continue

        columns = entry["columns"]

        # Accumulate records for tables with multiple INSERT blocks
        if table not in fixtures:
            fixtures[table] = []

        for row in entry["rows"]:
            pk = None
            fields = {}

            for col, val in zip(columns, row):
                if col.lower() == "id":
                    pk = val
                    continue

                field_name = col

                # Type conversions
                if col in BOOLEAN_FIELDS and val is not None:
                    val = bool(val)
                elif col in DECIMAL_FIELDS and isinstance(val, (int, float)):
                    val = str(val)

                fields[field_name] = val

            fixtures[table].append({"model": model, "pk": pk, "fields": fields})

    return fixtures


def write_fixtures(fixtures: dict[str, list[dict]]):
    """Write fixtures to JSON files."""
    FIXTURES_DIR.mkdir(exist_ok=True)

    for table, records in fixtures.items():
        out = FIXTURES_DIR / f"{table}.json"
        out.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  ✔  {out.name}  ({len(records)} records)")


def main():
    if not SQL_FILE.exists():
        print(f"  ✘  {SQL_FILE} not found.")
        raise SystemExit(1)

    print(f"  ℹ  Reading {SQL_FILE.name}...")
    sql_text = SQL_FILE.read_text(encoding="utf-8")

    print("  ℹ  Parsing INSERT statements...")
    parsed = parse_sql(sql_text)
    print(f"  ℹ  Found {len(parsed)} table(s)")

    print("  ℹ  Converting to Django fixtures...")
    fixtures = to_django_fixture(parsed)

    print(f"  ℹ  Writing to {FIXTURES_DIR}/")
    write_fixtures(fixtures)

    total = sum(len(v) for v in fixtures.values())
    print(f"\n  ✔  Done — {total} records across {len(fixtures)} fixture file(s).")


if __name__ == "__main__":
    main()
