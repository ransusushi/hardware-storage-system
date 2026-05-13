# User manual

The Hardware Storage System is a web app for managing a hardware inventory
business. Every change you make on the website is written immediately to the
MySQL database.

## 1. Signing in

1. Open the site (default <http://localhost:5000>).
2. Enter your **username** and **password** and click **Sign in**.

Seeded demo accounts (all use the password `password123`):

| Username  | Role     | What they can do                                                |
|-----------|----------|------------------------------------------------------------------|
| `admin`   | admin    | Everything, including creating / deleting staff accounts.        |
| `mlopez`  | manager  | Manage products, categories, suppliers, warehouses, stock, view staff, reports, queries. |
| `jdcruz`  | staff    | Create / edit customers and orders, view all data, view reports and queries. |
| `asantos` | staff    | Same as `jdcruz`.                                                |

If you are locked out, ask an admin to reset your password from
**Staff → Edit**.

## 2. Dashboard

The dashboard (the home page) shows:

- KPI cards for products, stock, warehouses, suppliers, customers, orders,
  staff, and total revenue from paid+shipped orders.
- A **low-stock alerts** panel listing items that are at or below their
  reorder level in any warehouse.
- A **recent orders** panel with the eight most recent orders.

Click any KPI card to jump straight to that section.

## 3. CRUD pages

Every primary table has its own page in the top navigation. Each page
follows the same pattern:

- **List** — table view with edit / delete buttons in the right column and a
  blue **Add** button in the top-right corner.
- **Add / Edit** — same form for creating and updating; click **Save** to
  write to MySQL.
- **Delete** — small red button on the list row; you are asked to confirm
  before the delete is sent. Deletes are blocked if other tables still
  reference the row (e.g. you cannot delete a category that still has
  products in it).

| Page         | Resource              | Roles that can write |
|--------------|------------------------|----------------------|
| Products     | hardware catalog       | admin, manager       |
| Stock        | per-warehouse quantity | admin, manager       |
| Categories   | product categories     | admin, manager       |
| Suppliers    | supplier directory     | admin, manager       |
| Warehouses   | physical locations     | admin, manager       |
| Customers    | retail and wholesale   | admin, manager, staff |
| Orders       | customer purchases     | admin, manager, staff |
| Staff        | employees + roles      | admin only (read: admin/manager) |

## 4. Working with orders

1. **Create an order:** Orders → **New order**, pick the customer and status.
2. The new order opens with an empty line items table.
3. **Add line items:** scroll to the *Add line item* card, pick a product,
   enter the quantity (the price defaults to the product's current unit
   price), and click **Add**. The order total is recomputed every time you
   add or remove an item.
4. **Change the order's status** (pending → paid → shipped) by clicking
   **Edit** on the order detail page, or from the orders list.
5. **Delete a line item** by clicking the small red × on its row.

## 5. Running queries

Open **Queries** in the top navigation. Each query card shows:

- The real-world business question (the *scenario*).
- The operations it demonstrates (selection, projection, ×, ∪, −).

Click a card to see:

- The exact **SQL** statement (and the MariaDB-equivalent the engine runs if
  the original used `EXCEPT`).
- A **stepwise relational-algebra** translation (intermediate relations
  `R1`, `R2`, …).
- The **compact** relational-algebra expression.
- A blue **Run query** button — clicking it executes the query against the
  live database and displays the result table below.

## 6. Reports

The **Reports** page shows five pre-built reports:

1. **Unified contact list** (UNION) — customers ∪ suppliers in a single list.
2. **Products never ordered** (DIFFERENCE).
3. **Customers without orders** (DIFFERENCE).
4. **High-value, non-cancelled orders** (AND / OR / NOT).
5. **Low stock report** (selection + projection).

Reports always show *live* data from MySQL.

## 7. Logging out

Click **Logout** at the top-right corner of any page.

## 8. Troubleshooting

- **"Invalid username or password"** — check capitalisation; passwords are
  case-sensitive. Default password is `password123`.
- **"Cannot delete category (referenced by products?)"** — clear the
  dependent rows first (products in this case), then retry the delete.
- **The website doesn't reflect my change** — refresh the page. Every CRUD
  action is committed to MySQL inside the same HTTP request, so the change
  is visible to the next query.
