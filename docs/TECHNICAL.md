# Technical documentation

## Stack

| Layer       | Technology                                   |
|-------------|-----------------------------------------------|
| Language    | Python 3.10+                                  |
| Web         | Flask 3.x (blueprint per resource)            |
| Templates   | Jinja2 + Bootstrap 5 + Bootstrap Icons        |
| Database    | MySQL 8.x or MariaDB 10.x (InnoDB, utf8mb4)   |
| DB driver   | PyMySQL                                       |
| Auth        | server-side sessions + bcrypt password hashes |
| Config      | `.env` file (python-dotenv)                   |

## High-level architecture

```
┌────────────────────┐    HTTP    ┌──────────────────────┐    SQL    ┌──────────┐
│  Browser (UI)      │ ───────▶  │ Flask app (Python)   │ ───────▶  │  MySQL   │
│  Bootstrap 5       │ ◀───────  │ blueprints, views,   │ ◀───────  │  DB      │
│  Jinja2 templates  │           │ Jinja2 templates     │           │          │
└────────────────────┘            └──────────────────────┘            └──────────┘
```

Each HTTP request:

1. Flask resolves the URL to a blueprint view.
2. `before_request` loads the logged-in user from the session.
3. The view function calls `query_all` / `query_one` / `execute` in
   `app/db.py`, which opens a request-scoped PyMySQL connection.
4. The view renders a Jinja2 template (or redirects).
5. `teardown_appcontext` closes the PyMySQL connection.

## Source layout

```
app/__init__.py           # Flask application factory; wires up blueprints,
                          # request hooks, and template globals.
app/config.py             # Configuration dataclass populated from os.environ.
app/db.py                 # PyMySQL connection helpers (query_all, query_one,
                          # execute, run_raw_select).
app/auth.py               # /auth/login + /auth/logout, hash_password,
                          # verify_password, @login_required, @role_required.
app/queries.py            # Catalog of (SQL, relational-algebra) pairs +
                          # MariaDB-runnable equivalents for EXCEPT.
app/views/*.py            # One blueprint per table:
                          #   dashboard, products, categories, suppliers,
                          #   warehouses, stock, customers, orders, employees,
                          #   queries, reports.
app/templates/...         # Per-blueprint subfolders + base.html + _macros.html.
app/static/css/app.css    # Custom Bootstrap theming.
sql/schema.sql            # DDL: drops & recreates `hardware_storage`.
sql/seed.sql              # Sample data.
scripts/init_db.py        # One-shot installer: runs schema, seed,
                          # and bcrypt-hashes 'password123' for every employee.
run.py                    # Dev entry point (Werkzeug dev server).
```

## Database design notes

See [SCHEMA.md](./SCHEMA.md) for the table-by-table breakdown and the
[ER diagram](./ER_DIAGRAM.md).

- All foreign keys are explicit `FOREIGN KEY ... REFERENCES` constraints.
- `ON DELETE RESTRICT` is the default; `stock` and `order_items` cascade
  with their parent (products, warehouses, orders) so that deleting an
  order cleans up its line items.
- Surrogate integer primary keys are used throughout.
- Natural keys are enforced via `UNIQUE` (e.g. `sku`, `username`, `email`,
  `(product_id, warehouse_id)` on `stock`).
- `CHECK` constraints prevent negative quantities and prices.

## Auth and access control

- Passwords are hashed with **bcrypt** (cost 12) via the `bcrypt` library.
  The DB only stores the hash; plaintext is never persisted.
- Sessions are signed with the `FLASK_SECRET_KEY` value from `.env`.
- `@login_required` redirects unauthenticated users to `/auth/login` with
  a `?next=` parameter so they bounce back to the page they wanted.
- `@role_required('admin', ...)` further restricts which roles can perform
  destructive actions:
    - **admin**: can edit/delete staff.
    - **manager**: can manage catalog data (products, categories, suppliers,
      warehouses, stock) and customers/orders.
    - **staff**: can manage customers and orders only.

## CRUD writes

Every `INSERT`, `UPDATE`, and `DELETE` goes through `app/db.py::execute()`,
which calls `conn.commit()` before returning. There is **no caching layer**
between the UI and MySQL — what you see on the website is exactly what
`SELECT` returns.

For composite operations (e.g. adding a line item to an order), the view
also calls `_recompute_total(order_id)` to keep the derived `total_amount`
in sync with the line items.

## Query execution module

`/queries` reads the in-memory catalog from `app/queries.py::QUERIES`.
Clicking **Run query** POSTs to the same URL; the view calls
`db.run_raw_select(sql)` and renders the column metadata + rows.

MariaDB does not implement the SQL standard `EXCEPT` operator, so the
catalog ships a `SQL_RUNNABLE_OVERRIDES` table mapping each difference
query to its `LEFT JOIN ... WHERE NULL` equivalent. The original
`EXCEPT` form is still shown to the user.

## Reports

`/reports` runs five queries built directly from the relational-algebra
operations the assignment asks for:

| Report                        | Operations exercised |
|-------------------------------|----------------------|
| Unified contact list          | π, ∪                 |
| Products never ordered        | π, −                 |
| Customers without orders      | π, −                 |
| High-value non-cancelled orders | σ (AND / OR / NOT) |
| Low stock report              | σ, π, join           |

## Running tests / linting

The project uses no external test harness; functional verification is
performed end-to-end through the web UI. A quick smoke test can be done
from the shell:

```bash
curl -c c.txt -b c.txt -X POST -d "username=admin&password=password123" \
     http://localhost:5000/auth/login -i

for url in / /products/ /stock/ /orders/ /reports/ /queries/; do
  curl -b c.txt -s -o /dev/null -w "%{http_code} $url\n" http://localhost:5000$url
done
```

## Deployment notes

- For production, replace `python run.py` with a real WSGI server, e.g.
  `gunicorn 'app:create_app()' --bind 0.0.0.0:8000 --workers 4`.
- Run behind nginx / Apache for TLS termination.
- Set a strong random `FLASK_SECRET_KEY` (32+ bytes).
- Restrict the MySQL user to only the schema it needs.
- Disable the Flask debug server (`debug=False` and `FLASK_DEBUG=0`).
