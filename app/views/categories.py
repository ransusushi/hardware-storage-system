"""CRUD views for the categories table."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..auth import login_required, role_required
from ..db import execute, query_all, query_one

bp = Blueprint("categories", __name__, url_prefix="/categories")


@bp.route("/")
@login_required
def list_view():
    rows = query_all("SELECT * FROM categories ORDER BY name")
    return render_template("categories/list.html", rows=rows)


@bp.route("/new", methods=("GET", "POST"))
@role_required("admin", "manager")
def create():
    if request.method == "POST":
        execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s)",
            (request.form["name"].strip(), request.form.get("description", "").strip() or None),
        )
        flash("Category created.", "success")
        return redirect(url_for("categories.list_view"))
    return render_template("categories/form.html", row=None)


@bp.route("/<int:category_id>/edit", methods=("GET", "POST"))
@role_required("admin", "manager")
def edit(category_id: int):
    row = query_one("SELECT * FROM categories WHERE category_id = %s", (category_id,))
    if row is None:
        flash("Category not found.", "warning")
        return redirect(url_for("categories.list_view"))
    if request.method == "POST":
        execute(
            "UPDATE categories SET name=%s, description=%s WHERE category_id=%s",
            (
                request.form["name"].strip(),
                request.form.get("description", "").strip() or None,
                category_id,
            ),
        )
        flash("Category updated.", "success")
        return redirect(url_for("categories.list_view"))
    return render_template("categories/form.html", row=row)


@bp.route("/<int:category_id>/delete", methods=("POST",))
@role_required("admin", "manager")
def delete(category_id: int):
    try:
        execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
        flash("Category deleted.", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Cannot delete category (referenced by products?). {exc}", "danger")
    return redirect(url_for("categories.list_view"))
