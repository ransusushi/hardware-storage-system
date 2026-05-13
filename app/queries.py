"""Catalog of SQL queries paired with their relational-algebra translations.

Each query has:
  - id, title, scenario (real-world business question)
  - operation (relational-algebra ops it demonstrates)
  - sql                : the SQL statement
  - stepwise_algebra   : sequence of intermediate relational-algebra expressions
  - compact_algebra    : single compact relational-algebra expression

Relational-algebra symbols used:
  sigma (selection)        sigma_<predicate>(R)
  pi    (projection)        pi_<attrs>(R)
  X     (Cartesian product) R X S
  U     (union)             R U S
  -     (difference)        R - S
  rho   (rename)            rho_<NewName>(R)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryEntry:
    id: str
    title: str
    scenario: str
    operations: str
    sql: str
    stepwise_algebra: list[str]
    compact_algebra: str


QUERIES: list[QueryEntry] = [
    QueryEntry(
        id="q1_select_and",
        title="High-priced CPUs (selection with AND)",
        scenario="List all CPU products that cost at least 15,000.",
        operations="Selection (AND)",
        sql=(
            "SELECT p.product_id, p.name, p.unit_price\n"
            "FROM products p JOIN categories c ON c.category_id = p.category_id\n"
            "WHERE c.name = 'CPU' AND p.unit_price >= 15000;"
        ),
        stepwise_algebra=[
            "R1 = sigma_{name = 'CPU'} (categories)",
            "R2 = products X R1",
            "R3 = sigma_{products.category_id = R1.category_id AND products.unit_price >= 15000} (R2)",
            "Result = pi_{product_id, name, unit_price} (R3)",
        ],
        compact_algebra=(
            "pi_{product_id, name, unit_price} ( "
            "sigma_{c.name = 'CPU' AND p.unit_price >= 15000 AND p.category_id = c.category_id} "
            "(products p X categories c) )"
        ),
    ),
    QueryEntry(
        id="q2_select_or",
        title="Storage OR GPU products (selection with OR)",
        scenario="Show products that are either Storage or GPU items.",
        operations="Selection (OR), Projection",
        sql=(
            "SELECT p.product_id, p.name, c.name AS category\n"
            "FROM products p JOIN categories c ON c.category_id = p.category_id\n"
            "WHERE c.name = 'Storage' OR c.name = 'GPU';"
        ),
        stepwise_algebra=[
            "R1 = sigma_{name = 'Storage' OR name = 'GPU'} (categories)",
            "R2 = products X R1",
            "R3 = sigma_{products.category_id = R1.category_id} (R2)",
            "Result = pi_{product_id, p.name, R1.name} (R3)",
        ],
        compact_algebra=(
            "pi_{product_id, p.name, c.name} ( "
            "sigma_{p.category_id = c.category_id AND (c.name = 'Storage' OR c.name = 'GPU')} "
            "(products p X categories c) )"
        ),
    ),
    QueryEntry(
        id="q3_select_not",
        title="Active staff who are NOT admins (selection with NOT)",
        scenario="List all active employees who do not hold the 'admin' role.",
        operations="Selection (NOT), Projection",
        sql=(
            "SELECT e.employee_id, e.full_name, r.role_name\n"
            "FROM employees e JOIN roles r ON r.role_id = e.role_id\n"
            "WHERE e.is_active = 1 AND NOT (r.role_name = 'admin');"
        ),
        stepwise_algebra=[
            "R1 = sigma_{NOT (role_name = 'admin')} (roles)",
            "R2 = sigma_{is_active = 1} (employees)",
            "R3 = R2 X R1",
            "R4 = sigma_{R2.role_id = R1.role_id} (R3)",
            "Result = pi_{employee_id, full_name, role_name} (R4)",
        ],
        compact_algebra=(
            "pi_{employee_id, full_name, role_name} ( "
            "sigma_{e.is_active = 1 AND NOT (r.role_name = 'admin') AND e.role_id = r.role_id} "
            "(employees e X roles r) )"
        ),
    ),
    QueryEntry(
        id="q4_projection",
        title="Customer contact list (projection)",
        scenario="Get only the names and emails of every customer.",
        operations="Projection",
        sql="SELECT full_name, email FROM customers;",
        stepwise_algebra=[
            "Result = pi_{full_name, email} (customers)",
        ],
        compact_algebra="pi_{full_name, email} (customers)",
    ),
    QueryEntry(
        id="q5_cartesian",
        title="Products in warehouses (Cartesian product + condition)",
        scenario=(
            "Pair every product with every warehouse and keep only the "
            "pairings that actually exist in the stock table for that warehouse."
        ),
        operations="Cartesian product (X), Selection, Projection",
        sql=(
            "SELECT p.name AS product, w.name AS warehouse, s.quantity\n"
            "FROM products p, warehouses w, stock s\n"
            "WHERE p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id\n"
            "      AND s.quantity > 0;"
        ),
        stepwise_algebra=[
            "R1 = products X warehouses",
            "R2 = R1 X stock",
            "R3 = sigma_{products.product_id = stock.product_id AND warehouses.warehouse_id = stock.warehouse_id AND stock.quantity > 0} (R2)",
            "Result = pi_{p.name, w.name, s.quantity} (R3)",
        ],
        compact_algebra=(
            "pi_{p.name, w.name, s.quantity} ( "
            "sigma_{p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id AND s.quantity > 0} "
            "(products p X warehouses w X stock s) )"
        ),
    ),
    QueryEntry(
        id="q6_cartesian_orders",
        title="Customers and the employees who served them (Cartesian + condition)",
        scenario=(
            "List every (customer, employee) pair where the employee actually "
            "took an order from that customer."
        ),
        operations="Cartesian product (X), Selection, Projection",
        sql=(
            "SELECT DISTINCT c.full_name AS customer, e.full_name AS employee\n"
            "FROM customers c, employees e, orders o\n"
            "WHERE o.customer_id = c.customer_id AND o.employee_id = e.employee_id;"
        ),
        stepwise_algebra=[
            "R1 = customers X employees",
            "R2 = R1 X orders",
            "R3 = sigma_{c.customer_id = o.customer_id AND e.employee_id = o.employee_id} (R2)",
            "Result = pi_{c.full_name, e.full_name} (R3)",
        ],
        compact_algebra=(
            "pi_{c.full_name, e.full_name} ( "
            "sigma_{c.customer_id = o.customer_id AND e.employee_id = o.employee_id} "
            "(customers c X employees e X orders o) )"
        ),
    ),
    QueryEntry(
        id="q7_union",
        title="People to contact (UNION of customers and suppliers)",
        scenario=(
            "Build a single contact list combining customer emails and supplier emails."
        ),
        operations="Projection, UNION",
        sql=(
            "SELECT full_name AS name, email FROM customers WHERE email IS NOT NULL\n"
            "UNION\n"
            "SELECT name        AS name, email FROM suppliers WHERE email IS NOT NULL;"
        ),
        stepwise_algebra=[
            "R1 = pi_{full_name, email} ( sigma_{email IS NOT NULL} (customers) )",
            "R2 = pi_{name, email}      ( sigma_{email IS NOT NULL} (suppliers) )",
            "R1' = rho_{name, email} (R1)",
            "Result = R1' U R2",
        ],
        compact_algebra=(
            "rho_{name, email} ( pi_{full_name, email} (sigma_{email IS NOT NULL} (customers)) ) "
            "U pi_{name, email} (sigma_{email IS NOT NULL} (suppliers))"
        ),
    ),
    QueryEntry(
        id="q8_difference",
        title="Products that have NEVER been ordered (DIFFERENCE)",
        scenario=(
            "Find products that exist in the catalog but have never appeared "
            "on an order line."
        ),
        operations="Projection, DIFFERENCE",
        sql=(
            "SELECT product_id FROM products\n"
            "EXCEPT\n"
            "SELECT product_id FROM order_items;"
        ),
        stepwise_algebra=[
            "R1 = pi_{product_id} (products)",
            "R2 = pi_{product_id} (order_items)",
            "Result = R1 - R2",
        ],
        compact_algebra="pi_{product_id} (products) - pi_{product_id} (order_items)",
    ),
    QueryEntry(
        id="q9_difference_customers",
        title="Customers who have not yet placed an order",
        scenario=(
            "Find customers in the database who have never placed an order."
        ),
        operations="Projection, DIFFERENCE",
        sql=(
            "SELECT customer_id FROM customers\n"
            "EXCEPT\n"
            "SELECT customer_id FROM orders;"
        ),
        stepwise_algebra=[
            "R1 = pi_{customer_id} (customers)",
            "R2 = pi_{customer_id} (orders)",
            "Result = R1 - R2",
        ],
        compact_algebra="pi_{customer_id} (customers) - pi_{customer_id} (orders)",
    ),
    QueryEntry(
        id="q10_complex_and_not",
        title="Paid orders from wholesale customers above 50,000 (AND + NOT)",
        scenario=(
            "Show paid orders worth more than 50,000 from wholesale customers, "
            "but NOT orders that have been cancelled."
        ),
        operations="Selection (AND/NOT), Projection",
        sql=(
            "SELECT o.order_id, c.full_name, o.total_amount, o.status\n"
            "FROM orders o JOIN customers c ON c.customer_id = o.customer_id\n"
            "WHERE c.customer_type = 'wholesale'\n"
            "  AND o.total_amount > 50000\n"
            "  AND NOT (o.status = 'cancelled');"
        ),
        stepwise_algebra=[
            "R1 = sigma_{customer_type = 'wholesale'} (customers)",
            "R2 = orders X R1",
            "R3 = sigma_{orders.customer_id = R1.customer_id AND total_amount > 50000 AND NOT (status = 'cancelled')} (R2)",
            "Result = pi_{order_id, full_name, total_amount, status} (R3)",
        ],
        compact_algebra=(
            "pi_{order_id, full_name, total_amount, status} ( "
            "sigma_{c.customer_type = 'wholesale' AND o.total_amount > 50000 "
            "AND NOT (o.status = 'cancelled') AND o.customer_id = c.customer_id} "
            "(orders o X customers c) )"
        ),
    ),
    QueryEntry(
        id="q11_union_low_stock",
        title="Low-stock items across two warehouses (UNION)",
        scenario=(
            "Get all products that are at/below their reorder level in "
            "either the Main Warehouse or the South Hub."
        ),
        operations="Selection, Projection, UNION",
        sql=(
            "SELECT p.name FROM products p, stock s, warehouses w\n"
            "WHERE p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id\n"
            "      AND w.name = 'Main Warehouse' AND s.quantity <= s.reorder_level\n"
            "UNION\n"
            "SELECT p.name FROM products p, stock s, warehouses w\n"
            "WHERE p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id\n"
            "      AND w.name = 'South Hub' AND s.quantity <= s.reorder_level;"
        ),
        stepwise_algebra=[
            "R1 = sigma_{w.name = 'Main Warehouse' AND s.quantity <= s.reorder_level AND p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id} (products p X stock s X warehouses w)",
            "R2 = sigma_{w.name = 'South Hub'      AND s.quantity <= s.reorder_level AND p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id} (products p X stock s X warehouses w)",
            "R1' = pi_{p.name} (R1)",
            "R2' = pi_{p.name} (R2)",
            "Result = R1' U R2'",
        ],
        compact_algebra=(
            "pi_{p.name} ( sigma_{w.name='Main Warehouse' AND s.quantity<=s.reorder_level AND p.product_id=s.product_id AND w.warehouse_id=s.warehouse_id} (P X S X W) ) "
            "U "
            "pi_{p.name} ( sigma_{w.name='South Hub' AND s.quantity<=s.reorder_level AND p.product_id=s.product_id AND w.warehouse_id=s.warehouse_id} (P X S X W) )"
        ),
    ),
    QueryEntry(
        id="q12_diff_supplier_local",
        title="Foreign suppliers (DIFFERENCE)",
        scenario=(
            "List suppliers that are NOT based in the Philippines."
        ),
        operations="Projection, DIFFERENCE",
        sql=(
            "SELECT supplier_id, name FROM suppliers\n"
            "EXCEPT\n"
            "SELECT supplier_id, name FROM suppliers WHERE country = 'Philippines';"
        ),
        stepwise_algebra=[
            "R1 = pi_{supplier_id, name} (suppliers)",
            "R2 = pi_{supplier_id, name} (sigma_{country = 'Philippines'} (suppliers))",
            "Result = R1 - R2",
        ],
        compact_algebra=(
            "pi_{supplier_id, name} (suppliers) - "
            "pi_{supplier_id, name} (sigma_{country = 'Philippines'} (suppliers))"
        ),
    ),
]


# MariaDB / MySQL do not support EXCEPT directly; provide LEFT-JOIN equivalents
# for the difference queries so the query runner can actually execute them.
SQL_RUNNABLE_OVERRIDES = {
    "q8_difference": (
        "SELECT p.product_id, p.name\n"
        "FROM products p\n"
        "LEFT JOIN order_items oi ON oi.product_id = p.product_id\n"
        "WHERE oi.product_id IS NULL;"
    ),
    "q9_difference_customers": (
        "SELECT c.customer_id, c.full_name\n"
        "FROM customers c\n"
        "LEFT JOIN orders o ON o.customer_id = c.customer_id\n"
        "WHERE o.customer_id IS NULL;"
    ),
    "q12_diff_supplier_local": (
        "SELECT supplier_id, name, country\n"
        "FROM suppliers\n"
        "WHERE country IS NULL OR country <> 'Philippines';"
    ),
}


def get_query(query_id: str) -> QueryEntry | None:
    for q in QUERIES:
        if q.id == query_id:
            return q
    return None


def runnable_sql(entry: QueryEntry) -> str:
    """Return SQL that the MariaDB/MySQL engine can actually execute."""
    return SQL_RUNNABLE_OVERRIDES.get(entry.id, entry.sql)
