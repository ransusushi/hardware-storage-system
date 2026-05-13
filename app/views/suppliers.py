"""CRUD views for suppliers."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..auth import login_required, role_required
from ..db import execute, query_all, query_one

bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")


@bp.route("/")
@login_required
def list_view():
    rows = query_all("SELECT * FROM suppliers ORDER BY name")
    return render_template("suppliers/list.html", rows=rows)


def _form_values():
    return (
        request.form["name"].strip(),
        request.form.get("contact_name", "").strip() or None,
        request.form.get("email", "").strip() or None,
        request.form.get("phone", "").strip() or None,
        request.form.get("address", "").strip() or None,
        request.form.get("country", "").strip() or None,
    )


@bp.route("/new", methods=("GET", "POST"))
@role_required("admin", "manager")
def create():
    if request.method == "POST":
        execute(
            """INSERT INTO suppliers (name, contact_name, email, phone, address, country)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            _form_values(),
        )
        flash("Supplier created.", "success")
        return redirect(url_for("suppliers.list_view"))
    return render_template("suppliers/form.html", row=None)


@bp.route("/<int:supplier_id>/edit", methods=("GET", "POST"))
@role_required("admin", "manager")
def edit(supplier_id: int):
    row = query_one("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
    if row is None:
        flash("Supplier not found.", "warning")
        return redirect(url_for("suppliers.list_view"))
    if request.method == "POST":
        execute(
            """UPDATE suppliers SET name=%s, contact_name=%s, email=%s, phone=%s,
               address=%s, country=%s WHERE supplier_id=%s""",
            (*_form_values(), supplier_id),
        )
        flash("Supplier updated.", "success")
        return redirect(url_for("suppliers.list_view"))
    return render_template("suppliers/form.html", row=row)


@bp.route("/<int:supplier_id>/delete", methods=("POST",))
@role_required("admin", "manager")
def delete(supplier_id: int):
    try:
        execute("DELETE FROM suppliers WHERE supplier_id=%s", (supplier_id,))
        flash("Supplier deleted.", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Cannot delete supplier. {exc}", "danger")
    return redirect(url_for("suppliers.list_view"))
