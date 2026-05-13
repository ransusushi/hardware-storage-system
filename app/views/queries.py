"""Query runner: lists every catalogued SQL+relational-algebra query
and lets staff execute it live against MySQL."""
from __future__ import annotations

from flask import Blueprint, abort, render_template, request

from ..auth import login_required
from ..db import run_raw_select
from ..queries import QUERIES, get_query, runnable_sql

bp = Blueprint("queries", __name__, url_prefix="/queries")


@bp.route("/")
@login_required
def list_view():
    return render_template("queries/list.html", queries=QUERIES)


@bp.route("/<qid>", methods=("GET", "POST"))
@login_required
def detail(qid: str):
    entry = get_query(qid)
    if entry is None:
        abort(404)

    columns: list[str] = []
    rows: list[list] = []
    error: str | None = None
    executed = False

    if request.method == "POST":
        try:
            columns, rows = run_raw_select(runnable_sql(entry))
            executed = True
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            executed = True

    return render_template(
        "queries/detail.html",
        entry=entry,
        executed=executed,
        columns=columns,
        rows=rows,
        error=error,
        runnable_sql=runnable_sql(entry),
    )
