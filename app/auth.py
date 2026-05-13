"""Authentication: login, logout, session, role-based access decorators."""
from __future__ import annotations

from functools import wraps
from typing import Callable

import bcrypt
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .db import query_one

bp = Blueprint("auth", __name__, url_prefix="/auth")


def hash_password(plain: str) -> str:
    """Hash a plain password with bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def load_current_user() -> None:
    """Populate g.user from the session, if logged in."""
    user_id = session.get("user_id")
    g.user = None
    if user_id is None:
        return
    g.user = query_one(
        """
        SELECT e.employee_id, e.username, e.full_name, e.email, e.is_active,
               r.role_name
        FROM employees e
        JOIN roles r ON r.role_id = e.role_id
        WHERE e.employee_id = %s
        """,
        (user_id,),
    )
    if not g.user or not g.user["is_active"]:
        session.clear()
        g.user = None


def login_required(view: Callable) -> Callable:
    """Decorator: require a logged-in employee."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if getattr(g, "user", None) is None:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles: str) -> Callable:
    """Decorator: require the logged-in user to have one of `roles`."""

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapped(*args, **kwargs):
            if getattr(g, "user", None) is None:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login", next=request.path))
            if g.user["role_name"] not in roles:
                flash("You do not have permission to perform that action.", "danger")
                return redirect(url_for("dashboard.index"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        row = query_one(
            """
            SELECT e.employee_id, e.username, e.password_hash, e.is_active, r.role_name
            FROM employees e
            JOIN roles r ON r.role_id = e.role_id
            WHERE e.username = %s
            """,
            (username,),
        )
        if row is None or not row["is_active"] or not verify_password(password, row["password_hash"]):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html", username=username), 401

        session.clear()
        session["user_id"] = row["employee_id"]
        session["role"] = row["role_name"]
        flash(f"Welcome back, {row['username']}!", "success")
        next_url = request.args.get("next") or url_for("dashboard.index")
        return redirect(next_url)

    return render_template("auth/login.html")


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
