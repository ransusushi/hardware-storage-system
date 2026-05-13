"""Dashboard / home view."""
from __future__ import annotations

from flask import Blueprint, render_template

from ..auth import login_required
from ..db import query_all, query_one

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    stats = {
        "products":   query_one("SELECT COUNT(*) AS c FROM products")["c"],
        "suppliers":  query_one("SELECT COUNT(*) AS c FROM suppliers")["c"],
        "customers":  query_one("SELECT COUNT(*) AS c FROM customers")["c"],
        "orders":     query_one("SELECT COUNT(*) AS c FROM orders")["c"],
        "warehouses": query_one("SELECT COUNT(*) AS c FROM warehouses")["c"],
        "employees":  query_one("SELECT COUNT(*) AS c FROM employees")["c"],
        "total_stock": query_one("SELECT COALESCE(SUM(quantity),0) AS c FROM stock")["c"],
        "revenue":    query_one(
            "SELECT COALESCE(SUM(total_amount),0) AS c FROM orders WHERE status IN ('paid','shipped')"
        )["c"],
    }
    low_stock = query_all(
        """
        SELECT p.name AS product, w.name AS warehouse, s.quantity, s.reorder_level
        FROM stock s
        JOIN products p   ON p.product_id = s.product_id
        JOIN warehouses w ON w.warehouse_id = s.warehouse_id
        WHERE s.quantity <= s.reorder_level
        ORDER BY s.quantity ASC
        LIMIT 10
        """
    )
    recent_orders = query_all(
        """
        SELECT o.order_id, o.order_date, o.status, o.total_amount,
               c.full_name AS customer, e.full_name AS handled_by
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        JOIN employees e ON e.employee_id = o.employee_id
        ORDER BY o.order_date DESC
        LIMIT 8
        """
    )
    return render_template(
        "dashboard.html",
        stats=stats,
        low_stock=low_stock,
        recent_orders=recent_orders,
    )
