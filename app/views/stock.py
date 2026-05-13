"""CRUD views for the stock (product-warehouse) table."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..auth import login_required, role_required
from ..db import execute, query_all, query_one

bp = Blueprint("stock", __name__, url_prefix="/stock")


@bp.route("/")
@login_required
def list_view():
    rows = query_all(
        """
        SELECT s.stock_id, s.quantity, s.reorder_level,
               p.product_id, p.name AS product, p.sku,
               w.warehouse_id, w.name AS warehouse,
               (s.quantity <= s.reorder_level) AS is_low
        FROM stock s
        JOIN products   p ON p.product_id = s.product_id
        JOIN warehouses w ON w.warehouse_id = s.warehouse_id
        ORDER BY w.name, p.name
        """
    )
    return render_template("stock/list.html", rows=rows)


def _form_values():
    return (
        int(request.form["product_id"]),
        int(request.form["warehouse_id"]),
        int(request.form.get("quantity", "0") or 0),
        int(request.form.get("reorder_level", "5") or 5),
    )


def _lookup():
    return {
        "products":   query_all("SELECT product_id, name, sku FROM products ORDER BY name"),
        "warehouses": query_all("SELECT warehouse_id, name FROM warehouses ORDER BY name"),
    }


@bp.route("/new", methods=("GET", "POST"))
@role_required("admin", "manager")
def create():
    if request.method == "POST":
        execute(
            """INSERT INTO stock (product_id, warehouse_id, quantity, reorder_level)
               VALUES (%s, %s, %s, %s)""",
            _form_values(),
        )
        flash("Stock entry created.", "success")
        return redirect(url_for("stock.list_view"))
    return render_template("stock/form.html", row=None, **_lookup())


@bp.route("/<int:stock_id>/edit", methods=("GET", "POST"))
@role_required("admin", "manager")
def edit(stock_id: int):
    row = query_one("SELECT * FROM stock WHERE stock_id = %s", (stock_id,))
    if row is None:
        flash("Stock entry not found.", "warning")
        return redirect(url_for("stock.list_view"))
    if request.method == "POST":
        execute(
            """UPDATE stock SET product_id=%s, warehouse_id=%s, quantity=%s, reorder_level=%s
               WHERE stock_id=%s""",
            (*_form_values(), stock_id),
        )
        flash("Stock updated.", "success")
        return redirect(url_for("stock.list_view"))
    return render_template("stock/form.html", row=row, **_lookup())


@bp.route("/<int:stock_id>/delete", methods=("POST",))
@role_required("admin", "manager")
def delete(stock_id: int):
    execute("DELETE FROM stock WHERE stock_id=%s", (stock_id,))
    flash("Stock entry deleted.", "success")
    return redirect(url_for("stock.list_view"))
