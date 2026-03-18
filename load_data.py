#!/usr/bin/env python
"""
Load seeding data into MariaDB database.
Run: python load_data.py
"""

import pymysql
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_data():
    # Connect to MariaDB
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="",
        charset="utf8mb4",
        autocommit=True,
    )

    sql_files = [
        ("Schema", BASE_DIR / "database.sql"),
        ("Seeding Data", BASE_DIR / "data_seeding.sql"),
    ]

    with conn.cursor() as cursor:
        for name, sql_file in sql_files:
            if not sql_file.exists():
                print(f"⚠️  File not found: {sql_file}")
                continue

            print(f"📄 Loading {name}...")
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # Split by semicolon and execute each statement
            for statement in sql_content.split(";"):
                statement = statement.strip()
                if statement and not statement.startswith("--"):
                    try:
                        cursor.execute(statement)
                    except pymysql.err.OperationalError as e:
                        if "already exists" in str(e).lower():
                            continue  # Skip if table already exists
                        print(f"   ⚠️  {e}")
                    except Exception as e:
                        print(f"   ⚠️  {e}")

            print(f"   ✅ {name} loaded")

    conn.close()
    print("\n🎉 Data loaded successfully!")


if __name__ == "__main__":
    load_data()
