"""CRUD views for warehouses."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..auth import login_required, role_required
from ..db import execute, query_all, query_one

bp = Blueprint("warehouses", __name__, url_prefix="/warehouses")


@bp.route("/")
@login_required
def list_view():
    rows = query_all("SELECT * FROM warehouses ORDER BY name")
    return render_template("warehouses/list.html", rows=rows)


def _form_values():
    return (
        request.form["name"].strip(),
        request.form["city"].strip(),
        request.form.get("address", "").strip() or None,
        int(request.form.get("capacity", "0") or 0),
    )


@bp.route("/new", methods=("GET", "POST"))
@role_required("admin", "manager")
def create():
    if request.method == "POST":
        execute(
            "INSERT INTO warehouses (name, city, address, capacity) VALUES (%s, %s, %s, %s)",
            _form_values(),
        )
        flash("Warehouse created.", "success")
        return redirect(url_for("warehouses.list_view"))
    return render_template("warehouses/form.html", row=None)


@bp.route("/<int:warehouse_id>/edit", methods=("GET", "POST"))
@role_required("admin", "manager")
def edit(warehouse_id: int):
    row = query_one("SELECT * FROM warehouses WHERE warehouse_id = %s", (warehouse_id,))
    if row is None:
        flash("Warehouse not found.", "warning")
        return redirect(url_for("warehouses.list_view"))
    if request.method == "POST":
        execute(
            "UPDATE warehouses SET name=%s, city=%s, address=%s, capacity=%s WHERE warehouse_id=%s",
            (*_form_values(), warehouse_id),
        )
        flash("Warehouse updated.", "success")
        return redirect(url_for("warehouses.list_view"))
    return render_template("warehouses/form.html", row=row)


@bp.route("/<int:warehouse_id>/delete", methods=("POST",))
@role_required("admin", "manager")
def delete(warehouse_id: int):
    try:
        execute("DELETE FROM warehouses WHERE warehouse_id=%s", (warehouse_id,))
        flash("Warehouse deleted.", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Cannot delete warehouse. {exc}", "danger")
    return redirect(url_for("warehouses.list_view"))
