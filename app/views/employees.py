"""CRUD views for employees (staff)."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..auth import hash_password, login_required, role_required
from ..db import execute, query_all, query_one

bp = Blueprint("employees", __name__, url_prefix="/employees")


@bp.route("/")
@login_required
@role_required("admin", "manager")
def list_view():
    rows = query_all(
        """
        SELECT e.employee_id, e.username, e.full_name, e.email, e.phone,
               e.is_active, e.hired_on, r.role_name
        FROM employees e
        JOIN roles r ON r.role_id = e.role_id
        ORDER BY e.full_name
        """
    )
    return render_template("employees/list.html", rows=rows)


def _lookup():
    return {"roles": query_all("SELECT role_id, role_name FROM roles ORDER BY role_name")}


@bp.route("/new", methods=("GET", "POST"))
@role_required("admin")
def create():
    if request.method == "POST":
        execute(
            """INSERT INTO employees (username, password_hash, full_name, email, phone, role_id, is_active)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                request.form["username"].strip(),
                hash_password(request.form["password"]),
                request.form["full_name"].strip(),
                request.form["email"].strip(),
                request.form.get("phone", "").strip() or None,
                int(request.form["role_id"]),
                1 if request.form.get("is_active") == "on" else 0,
            ),
        )
        flash("Employee created.", "success")
        return redirect(url_for("employees.list_view"))
    return render_template("employees/form.html", row=None, **_lookup())


@bp.route("/<int:employee_id>/edit", methods=("GET", "POST"))
@role_required("admin")
def edit(employee_id: int):
    row = query_one("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
    if row is None:
        flash("Employee not found.", "warning")
        return redirect(url_for("employees.list_view"))
    if request.method == "POST":
        new_password = request.form.get("password", "").strip()
        if new_password:
            execute(
                """UPDATE employees SET username=%s, password_hash=%s, full_name=%s, email=%s,
                   phone=%s, role_id=%s, is_active=%s WHERE employee_id=%s""",
                (
                    request.form["username"].strip(),
                    hash_password(new_password),
                    request.form["full_name"].strip(),
                    request.form["email"].strip(),
                    request.form.get("phone", "").strip() or None,
                    int(request.form["role_id"]),
                    1 if request.form.get("is_active") == "on" else 0,
                    employee_id,
                ),
            )
        else:
            execute(
                """UPDATE employees SET username=%s, full_name=%s, email=%s,
                   phone=%s, role_id=%s, is_active=%s WHERE employee_id=%s""",
                (
                    request.form["username"].strip(),
                    request.form["full_name"].strip(),
                    request.form["email"].strip(),
                    request.form.get("phone", "").strip() or None,
                    int(request.form["role_id"]),
                    1 if request.form.get("is_active") == "on" else 0,
                    employee_id,
                ),
            )
        flash("Employee updated.", "success")
        return redirect(url_for("employees.list_view"))
    return render_template("employees/form.html", row=row, **_lookup())


@bp.route("/<int:employee_id>/delete", methods=("POST",))
@role_required("admin")
def delete(employee_id: int):
    try:
        execute("DELETE FROM employees WHERE employee_id=%s", (employee_id,))
        flash("Employee deleted.", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Cannot delete employee (handled orders?). {exc}", "danger")
    return redirect(url_for("employees.list_view"))
