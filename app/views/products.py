"""CRUD views for products."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..auth import login_required, role_required
from ..db import execute, query_all, query_one

bp = Blueprint("products", __name__, url_prefix="/products")


def _lookup():
    return {
        "categories": query_all("SELECT category_id, name FROM categories ORDER BY name"),
        "suppliers":  query_all("SELECT supplier_id, name FROM suppliers ORDER BY name"),
    }


@bp.route("/")
@login_required
def list_view():
    q = (request.args.get("q") or "").strip()
    category_id = request.args.get("category_id") or ""
    params: list = []
    sql = """
        SELECT p.*, c.name AS category, s.name AS supplier
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        JOIN suppliers  s ON s.supplier_id = p.supplier_id
        WHERE 1=1
    """
    if q:
        sql += " AND (p.name LIKE %s OR p.sku LIKE %s)"
        params.extend([f"%{q}%", f"%{q}%"])
    if category_id:
        sql += " AND p.category_id = %s"
        params.append(category_id)
    sql += " ORDER BY p.name"
    rows = query_all(sql, params)
    return render_template(
        "products/list.html",
        rows=rows,
        q=q,
        category_id=category_id,
        categories=query_all("SELECT category_id, name FROM categories ORDER BY name"),
    )


def _form_values():
    try:
        unit_price = Decimal(request.form.get("unit_price", "0") or "0")
    except InvalidOperation:
        unit_price = Decimal("0")
    return (
        request.form["sku"].strip().upper(),
        request.form["name"].strip(),
        int(request.form["category_id"]),
        int(request.form["supplier_id"]),
        unit_price,
        request.form.get("description", "").strip() or None,
    )


@bp.route("/new", methods=("GET", "POST"))
@role_required("admin", "manager")
def create():
    if request.method == "POST":
        execute(
            """INSERT INTO products (sku, name, category_id, supplier_id, unit_price, description)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            _form_values(),
        )
        flash("Product created.", "success")
        return redirect(url_for("products.list_view"))
    return render_template("products/form.html", row=None, **_lookup())


@bp.route("/<int:product_id>/edit", methods=("GET", "POST"))
@role_required("admin", "manager")
def edit(product_id: int):
    row = query_one("SELECT * FROM products WHERE product_id = %s", (product_id,))
    if row is None:
        flash("Product not found.", "warning")
        return redirect(url_for("products.list_view"))
    if request.method == "POST":
        execute(
            """UPDATE products SET sku=%s, name=%s, category_id=%s, supplier_id=%s,
               unit_price=%s, description=%s WHERE product_id=%s""",
            (*_form_values(), product_id),
        )
        flash("Product updated.", "success")
        return redirect(url_for("products.list_view"))
    return render_template("products/form.html", row=row, **_lookup())


@bp.route("/<int:product_id>/delete", methods=("POST",))
@role_required("admin", "manager")
def delete(product_id: int):
    try:
        execute("DELETE FROM products WHERE product_id=%s", (product_id,))
        flash("Product deleted.", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Cannot delete product. {exc}", "danger")
    return redirect(url_for("products.list_view"))
