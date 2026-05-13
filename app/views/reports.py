"""Reports page: precomputed reports built from UNION, DIFFERENCE,
and complex conditions."""
from __future__ import annotations

from flask import Blueprint, render_template

from ..auth import login_required
from ..db import query_all

bp = Blueprint("reports", __name__, url_prefix="/reports")


@bp.route("/")
@login_required
def index():
    # Report 1: UNION - unified contact list
    contacts = query_all(
        """
        SELECT full_name AS name, email, 'Customer' AS source
        FROM customers WHERE email IS NOT NULL
        UNION
        SELECT name AS name, email, 'Supplier' AS source
        FROM suppliers WHERE email IS NOT NULL
        ORDER BY source, name
        """
    )

    # Report 2: DIFFERENCE - products never ordered
    unsold = query_all(
        """
        SELECT p.product_id, p.sku, p.name, c.name AS category
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        LEFT JOIN order_items oi ON oi.product_id = p.product_id
        WHERE oi.product_id IS NULL
        ORDER BY p.name
        """
    )

    # Report 3: DIFFERENCE - customers who never placed an order
    dormant_customers = query_all(
        """
        SELECT c.customer_id, c.full_name, c.email, c.customer_type
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.customer_id
        WHERE o.customer_id IS NULL
        ORDER BY c.full_name
        """
    )

    # Report 4: complex condition (AND/OR/NOT) - high value, non-cancelled orders
    big_orders = query_all(
        """
        SELECT o.order_id, c.full_name AS customer, o.total_amount, o.status, o.order_date
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        WHERE o.total_amount > 20000
          AND NOT (o.status = 'cancelled')
          AND (c.customer_type = 'wholesale' OR o.total_amount > 50000)
        ORDER BY o.total_amount DESC
        """
    )

    # Report 5: low-stock report (selection + projection)
    low_stock = query_all(
        """
        SELECT p.name AS product, w.name AS warehouse, s.quantity, s.reorder_level
        FROM stock s
        JOIN products p   ON p.product_id   = s.product_id
        JOIN warehouses w ON w.warehouse_id = s.warehouse_id
        WHERE s.quantity <= s.reorder_level
        ORDER BY s.quantity ASC
        """
    )

    return render_template(
        "reports/index.html",
        contacts=contacts,
        unsold=unsold,
        dormant_customers=dormant_customers,
        big_orders=big_orders,
        low_stock=low_stock,
    )
