"""MySQL connection helpers."""
from __future__ import annotations

from typing import Any, Iterable

import pymysql
from flask import current_app, g


def get_connection() -> pymysql.connections.Connection:
    """Return a request-scoped MySQL connection."""
    if "db_conn" not in g:
        cfg = current_app.config
        g.db_conn = pymysql.connect(
            host=cfg["MYSQL_HOST"],
            port=cfg["MYSQL_PORT"],
            user=cfg["MYSQL_USER"],
            password=cfg["MYSQL_PASSWORD"],
            database=cfg["MYSQL_DB"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    return g.db_conn


def close_connection(_exc: BaseException | None = None) -> None:
    """Close the request-scoped MySQL connection."""
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def query_all(sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    """Run a SELECT and return all rows as dicts."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        return list(cur.fetchall())


def query_one(sql: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
    """Run a SELECT and return the first row, or None."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        row = cur.fetchone()
    return row


def execute(sql: str, params: Iterable[Any] | None = None) -> int:
    """Run an INSERT/UPDATE/DELETE and return the lastrowid (for inserts) or rowcount."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        last_id = cur.lastrowid
        rowcount = cur.rowcount
    conn.commit()
    return last_id or rowcount


def run_raw_select(sql: str) -> tuple[list[str], list[list[Any]]]:
    """Execute an arbitrary SELECT for the query runner. Returns (columns, rows)."""
    conn = get_connection()
    with conn.cursor(pymysql.cursors.Cursor) as cur:
        cur.execute(sql)
        rows = list(cur.fetchall())
        columns = [d[0] for d in cur.description] if cur.description else []
    return columns, [list(r) for r in rows]
