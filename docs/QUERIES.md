# SQL queries and relational-algebra translations

This document maps every query in the system to a real-world scenario,
its SQL implementation, and its relational-algebra translation
(both the **stepwise** form using intermediate relations and the **compact**
single-expression form).

> **Notation** &nbsp; σ = selection &nbsp; π = projection &nbsp; × = Cartesian product &nbsp;
> ∪ = union &nbsp; − = difference &nbsp; ρ = rename.
> Because GitHub markdown rarely renders Greek letters consistently, the queries
> in code also use ASCII spellings: `sigma`, `pi`, `X`, `U`, `-`, `rho`.

The same catalog is rendered live in the application at **`/queries`**, where
each query can be executed against the live database with a single click.

---

## 1. High-priced CPUs (selection with AND)

**Scenario:** List all CPU products that cost at least 15,000.
**Operations:** σ (AND), π.

```sql
SELECT p.product_id, p.name, p.unit_price
FROM products p JOIN categories c ON c.category_id = p.category_id
WHERE c.name = 'CPU' AND p.unit_price >= 15000;
```

Stepwise:
```
R1 = sigma_{name = 'CPU'} (categories)
R2 = products X R1
R3 = sigma_{products.category_id = R1.category_id AND products.unit_price >= 15000} (R2)
Result = pi_{product_id, name, unit_price} (R3)
```

Compact:
```
pi_{product_id, name, unit_price} (
  sigma_{c.name = 'CPU' AND p.unit_price >= 15000 AND p.category_id = c.category_id}
        (products p X categories c)
)
```

---

## 2. Storage OR GPU products (selection with OR)

**Scenario:** Show products that are either Storage or GPU items.
**Operations:** σ (OR), π.

```sql
SELECT p.product_id, p.name, c.name AS category
FROM products p JOIN categories c ON c.category_id = p.category_id
WHERE c.name = 'Storage' OR c.name = 'GPU';
```

Stepwise:
```
R1 = sigma_{name = 'Storage' OR name = 'GPU'} (categories)
R2 = products X R1
R3 = sigma_{products.category_id = R1.category_id} (R2)
Result = pi_{product_id, p.name, R1.name} (R3)
```

Compact:
```
pi_{product_id, p.name, c.name} (
  sigma_{p.category_id = c.category_id AND (c.name = 'Storage' OR c.name = 'GPU')}
        (products p X categories c)
)
```

---

## 3. Active staff who are NOT admins (selection with NOT)

**Scenario:** List all active employees who do not hold the 'admin' role.
**Operations:** σ (NOT), π.

```sql
SELECT e.employee_id, e.full_name, r.role_name
FROM employees e JOIN roles r ON r.role_id = e.role_id
WHERE e.is_active = 1 AND NOT (r.role_name = 'admin');
```

Stepwise:
```
R1 = sigma_{NOT (role_name = 'admin')} (roles)
R2 = sigma_{is_active = 1} (employees)
R3 = R2 X R1
R4 = sigma_{R2.role_id = R1.role_id} (R3)
Result = pi_{employee_id, full_name, role_name} (R4)
```

Compact:
```
pi_{employee_id, full_name, role_name} (
  sigma_{e.is_active = 1 AND NOT (r.role_name = 'admin') AND e.role_id = r.role_id}
        (employees e X roles r)
)
```

---

## 4. Customer contact list (projection)

**Scenario:** Get only the names and emails of every customer.
**Operations:** π.

```sql
SELECT full_name, email FROM customers;
```

```
Result = pi_{full_name, email} (customers)
```

---

## 5. Products in warehouses (Cartesian product + condition)

**Scenario:** Pair every product with every warehouse and keep only the
pairings that actually exist in the stock table for that warehouse.
**Operations:** ×, σ, π.

```sql
SELECT p.name AS product, w.name AS warehouse, s.quantity
FROM products p, warehouses w, stock s
WHERE p.product_id = s.product_id
  AND w.warehouse_id = s.warehouse_id
  AND s.quantity > 0;
```

Stepwise:
```
R1 = products X warehouses
R2 = R1 X stock
R3 = sigma_{products.product_id = stock.product_id
            AND warehouses.warehouse_id = stock.warehouse_id
            AND stock.quantity > 0} (R2)
Result = pi_{p.name, w.name, s.quantity} (R3)
```

Compact:
```
pi_{p.name, w.name, s.quantity} (
  sigma_{p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id AND s.quantity > 0}
        (products p X warehouses w X stock s)
)
```

---

## 6. Customers and the employees who served them (Cartesian + condition)

**Scenario:** List every (customer, employee) pair where the employee actually
took an order from that customer.

```sql
SELECT DISTINCT c.full_name AS customer, e.full_name AS employee
FROM customers c, employees e, orders o
WHERE o.customer_id = c.customer_id AND o.employee_id = e.employee_id;
```

Stepwise:
```
R1 = customers X employees
R2 = R1 X orders
R3 = sigma_{c.customer_id = o.customer_id AND e.employee_id = o.employee_id} (R2)
Result = pi_{c.full_name, e.full_name} (R3)
```

Compact:
```
pi_{c.full_name, e.full_name} (
  sigma_{c.customer_id = o.customer_id AND e.employee_id = o.employee_id}
        (customers c X employees e X orders o)
)
```

---

## 7. People to contact (UNION of customers and suppliers)

**Scenario:** Build a single contact list combining customer emails and
supplier emails.
**Operations:** π, ∪.

```sql
SELECT full_name AS name, email FROM customers WHERE email IS NOT NULL
UNION
SELECT name        AS name, email FROM suppliers WHERE email IS NOT NULL;
```

Stepwise:
```
R1 = pi_{full_name, email} ( sigma_{email IS NOT NULL} (customers) )
R2 = pi_{name, email}      ( sigma_{email IS NOT NULL} (suppliers) )
R1' = rho_{name, email} (R1)
Result = R1' U R2
```

Compact:
```
rho_{name, email} ( pi_{full_name, email} (sigma_{email IS NOT NULL} (customers)) )
U
pi_{name, email} (sigma_{email IS NOT NULL} (suppliers))
```

---

## 8. Products that have NEVER been ordered (DIFFERENCE)

**Scenario:** Find products that exist in the catalog but have never appeared
on an order line.
**Operations:** π, −.

```sql
SELECT product_id FROM products
EXCEPT
SELECT product_id FROM order_items;
```

> MariaDB does not implement `EXCEPT` directly. The system runs the
> semantically equivalent left-anti-join:
> ```sql
> SELECT p.product_id, p.name FROM products p
> LEFT JOIN order_items oi ON oi.product_id = p.product_id
> WHERE oi.product_id IS NULL;
> ```

```
R1 = pi_{product_id} (products)
R2 = pi_{product_id} (order_items)
Result = R1 - R2
```

Compact:
```
pi_{product_id} (products) - pi_{product_id} (order_items)
```

---

## 9. Customers who have not yet placed an order

```sql
SELECT customer_id FROM customers
EXCEPT
SELECT customer_id FROM orders;
```

```
R1 = pi_{customer_id} (customers)
R2 = pi_{customer_id} (orders)
Result = R1 - R2
```

Compact:
```
pi_{customer_id} (customers) - pi_{customer_id} (orders)
```

---

## 10. Paid orders from wholesale customers above 50,000 (AND + NOT)

```sql
SELECT o.order_id, c.full_name, o.total_amount, o.status
FROM orders o JOIN customers c ON c.customer_id = o.customer_id
WHERE c.customer_type = 'wholesale'
  AND o.total_amount > 50000
  AND NOT (o.status = 'cancelled');
```

Stepwise:
```
R1 = sigma_{customer_type = 'wholesale'} (customers)
R2 = orders X R1
R3 = sigma_{orders.customer_id = R1.customer_id
            AND total_amount > 50000
            AND NOT (status = 'cancelled')} (R2)
Result = pi_{order_id, full_name, total_amount, status} (R3)
```

Compact:
```
pi_{order_id, full_name, total_amount, status} (
  sigma_{c.customer_type = 'wholesale'
         AND o.total_amount > 50000
         AND NOT (o.status = 'cancelled')
         AND o.customer_id = c.customer_id}
        (orders o X customers c)
)
```

---

## 11. Low-stock items across two warehouses (UNION)

```sql
SELECT p.name FROM products p, stock s, warehouses w
WHERE p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id
  AND w.name = 'Main Warehouse' AND s.quantity <= s.reorder_level
UNION
SELECT p.name FROM products p, stock s, warehouses w
WHERE p.product_id = s.product_id AND w.warehouse_id = s.warehouse_id
  AND w.name = 'South Hub' AND s.quantity <= s.reorder_level;
```

Stepwise:
```
R1 = sigma_{w.name = 'Main Warehouse' AND s.quantity <= s.reorder_level
            AND p.product_id = s.product_id
            AND w.warehouse_id = s.warehouse_id}
            (products p X stock s X warehouses w)
R2 = sigma_{w.name = 'South Hub' AND s.quantity <= s.reorder_level
            AND p.product_id = s.product_id
            AND w.warehouse_id = s.warehouse_id}
            (products p X stock s X warehouses w)
R1' = pi_{p.name} (R1)
R2' = pi_{p.name} (R2)
Result = R1' U R2'
```

Compact:
```
pi_{p.name} ( sigma_{w.name='Main Warehouse' AND s.quantity<=s.reorder_level
                     AND p.product_id=s.product_id
                     AND w.warehouse_id=s.warehouse_id}
              (P X S X W) )
U
pi_{p.name} ( sigma_{w.name='South Hub' AND s.quantity<=s.reorder_level
                     AND p.product_id=s.product_id
                     AND w.warehouse_id=s.warehouse_id}
              (P X S X W) )
```

---

## 12. Foreign suppliers (DIFFERENCE)

```sql
SELECT supplier_id, name FROM suppliers
EXCEPT
SELECT supplier_id, name FROM suppliers WHERE country = 'Philippines';
```

```
R1 = pi_{supplier_id, name} (suppliers)
R2 = pi_{supplier_id, name} (sigma_{country = 'Philippines'} (suppliers))
Result = R1 - R2
```

Compact:
```
pi_{supplier_id, name} (suppliers)
- pi_{supplier_id, name} (sigma_{country = 'Philippines'} (suppliers))
```
