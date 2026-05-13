"""Initialise the MySQL database: create schema, seed data, and (re)set passwords.

Usage:
    python scripts/init_db.py        # create schema + seed if DB is empty
    python scripts/init_db.py --reset  # drop & recreate everything
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import bcrypt
import pymysql
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "sql" / "schema.sql"
SEED   = ROOT / "sql" / "seed.sql"


def _connect(database: str | None = None):
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", "rootpass"),
        database=database,
        autocommit=True,
    )


def _run_script(sql_path: Path) -> None:
    """Execute a multi-statement SQL script."""
    text = sql_path.read_text(encoding="utf-8")
    statements = []
    buf = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue
        buf.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(buf))
            buf = []
    if buf:
        statements.append("\n".join(buf))
    conn = _connect()
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
    finally:
        conn.close()


def _reset_passwords() -> None:
    """Hash the literal password 'password123' for every seeded employee."""
    pw_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode()
    conn = _connect(os.environ.get("MYSQL_DB", "hardware_storage"))
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE employees SET password_hash = %s", (pw_hash,))
    finally:
        conn.close()


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="drop and recreate")
    args = parser.parse_args()

    print("Creating schema…")
    _run_script(SCHEMA)
    print("Seeding data…")
    _run_script(SEED)
    print("Resetting employee passwords to 'password123'…")
    _reset_passwords()
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
