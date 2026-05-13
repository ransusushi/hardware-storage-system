"""CRUD views for orders (header + line items)."""
from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from ..auth import login_required, role_required
from ..db import execute, query_all, query_one

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/")
@login_required
def list_view():
    rows = query_all(
        """
        SELECT o.order_id, o.order_date, o.status, o.total_amount,
               c.full_name AS customer, e.full_name AS employee
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        JOIN employees e ON e.employee_id = o.employee_id
        ORDER BY o.order_date DESC
        """
    )
    return render_template("orders/list.html", rows=rows)


@bp.route("/<int:order_id>")
@login_required
def detail(order_id: int):
    order = query_one(
        """
        SELECT o.*, c.full_name AS customer, c.email AS customer_email,
               e.full_name AS employee
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        JOIN employees e ON e.employee_id = o.employee_id
        WHERE o.order_id = %s
        """,
        (order_id,),
    )
    if order is None:
        flash("Order not found.", "warning")
        return redirect(url_for("orders.list_view"))
    items = query_all(
        """
        SELECT oi.*, p.name AS product, p.sku,
               (oi.quantity * oi.unit_price) AS line_total
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        WHERE oi.order_id = %s
        ORDER BY oi.order_item_id
        """,
        (order_id,),
    )
    products = query_all(
        "SELECT product_id, sku, name, unit_price FROM products ORDER BY name"
    )
    return render_template("orders/detail.html", order=order, items=items, products=products)


@bp.route("/new", methods=("GET", "POST"))
@role_required("admin", "manager", "staff")
def create():
    if request.method == "POST":
        customer_id = int(request.form["customer_id"])
        status = request.form.get("status", "pending")
        execute(
            """INSERT INTO orders (customer_id, employee_id, status, total_amount)
               VALUES (%s, %s, %s, 0)""",
            (customer_id, g.user["employee_id"], status),
        )
        new_id = query_one("SELECT LAST_INSERT_ID() AS id")["id"]
        flash("Order created. Add line items below.", "success")
        return redirect(url_for("orders.detail", order_id=new_id))
    customers = query_all("SELECT customer_id, full_name FROM customers ORDER BY full_name")
    return render_template("orders/form.html", row=None, customers=customers)


@bp.route("/<int:order_id>/edit", methods=("GET", "POST"))
@role_required("admin", "manager", "staff")
def edit(order_id: int):
    order = query_one("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    if order is None:
        flash("Order not found.", "warning")
        return redirect(url_for("orders.list_view"))
    if request.method == "POST":
        execute(
            "UPDATE orders SET customer_id=%s, status=%s WHERE order_id=%s",
            (int(request.form["customer_id"]), request.form["status"], order_id),
        )
        flash("Order updated.", "success")
        return redirect(url_for("orders.detail", order_id=order_id))
    customers = query_all("SELECT customer_id, full_name FROM customers ORDER BY full_name")
    return render_template("orders/form.html", row=order, customers=customers)


@bp.route("/<int:order_id>/delete", methods=("POST",))
@role_required("admin", "manager")
def delete(order_id: int):
    execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
    flash("Order deleted.", "success")
    return redirect(url_for("orders.list_view"))


def _recompute_total(order_id: int) -> None:
    """Recalculate the order's total_amount from its line items."""
    row = query_one(
        "SELECT COALESCE(SUM(quantity * unit_price), 0) AS total FROM order_items WHERE order_id=%s",
        (order_id,),
    )
    execute(
        "UPDATE orders SET total_amount=%s WHERE order_id=%s",
        (row["total"], order_id),
    )


@bp.route("/<int:order_id>/items/new", methods=("POST",))
@role_required("admin", "manager", "staff")
def add_item(order_id: int):
    product_id = int(request.form["product_id"])
    quantity = int(request.form["quantity"])
    product = query_one("SELECT unit_price FROM products WHERE product_id=%s", (product_id,))
    if product is None:
        flash("Product not found.", "danger")
        return redirect(url_for("orders.detail", order_id=order_id))
    unit_price = Decimal(str(request.form.get("unit_price") or product["unit_price"]))
    try:
        execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            (order_id, product_id, quantity, unit_price),
        )
        _recompute_total(order_id)
        flash("Item added.", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Could not add item (duplicate product?). {exc}", "danger")
    return redirect(url_for("orders.detail", order_id=order_id))


@bp.route("/<int:order_id>/items/<int:order_item_id>/delete", methods=("POST",))
@role_required("admin", "manager", "staff")
def delete_item(order_id: int, order_item_id: int):
    execute("DELETE FROM order_items WHERE order_item_id=%s AND order_id=%s",
            (order_item_id, order_id))
    _recompute_total(order_id)
    flash("Item removed.", "success")
    return redirect(url_for("orders.detail", order_id=order_id))
