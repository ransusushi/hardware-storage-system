# Database schema

Database name: **`hardware_storage`** (MySQL / MariaDB, InnoDB, `utf8mb4`)

10 tables. All foreign keys are declared `ON UPDATE CASCADE` with
`ON DELETE RESTRICT` or `ON DELETE CASCADE` where appropriate.

## Tables

### 1. `roles`
| Column      | Type            | Constraints              |
|-------------|-----------------|--------------------------|
| role_id     | INT             | **PK**, AUTO_INCREMENT   |
| role_name   | VARCHAR(50)     | NOT NULL, **UNIQUE**     |
| description | VARCHAR(255)    | NULL                     |

### 2. `employees`
| Column        | Type         | Constraints                                 |
|---------------|--------------|---------------------------------------------|
| employee_id   | INT          | **PK**, AUTO_INCREMENT                      |
| username      | VARCHAR(50)  | NOT NULL, **UNIQUE**                        |
| password_hash | VARCHAR(255) | NOT NULL (bcrypt)                           |
| full_name     | VARCHAR(100) | NOT NULL                                    |
| email         | VARCHAR(120) | NOT NULL, **UNIQUE**                        |
| phone         | VARCHAR(30)  | NULL                                        |
| role_id       | INT          | NOT NULL, **FK** → `roles.role_id`          |
| is_active     | TINYINT(1)   | NOT NULL DEFAULT 1                          |
| hired_on      | DATE         | NOT NULL DEFAULT CURRENT_DATE               |

### 3. `categories`
| Column      | Type         | Constraints           |
|-------------|--------------|-----------------------|
| category_id | INT          | **PK**, AUTO_INCREMENT|
| name        | VARCHAR(80)  | NOT NULL, **UNIQUE**  |
| description | VARCHAR(255) | NULL                  |

### 4. `suppliers`
| Column       | Type         | Constraints                |
|--------------|--------------|----------------------------|
| supplier_id  | INT          | **PK**, AUTO_INCREMENT     |
| name         | VARCHAR(120) | NOT NULL, **UNIQUE**       |
| contact_name | VARCHAR(100) | NULL                       |
| email        | VARCHAR(120) | NULL                       |
| phone        | VARCHAR(30)  | NULL                       |
| address      | VARCHAR(255) | NULL                       |
| country      | VARCHAR(60)  | NULL                       |

### 5. `warehouses`
| Column       | Type         | Constraints                       |
|--------------|--------------|-----------------------------------|
| warehouse_id | INT          | **PK**, AUTO_INCREMENT            |
| name         | VARCHAR(80)  | NOT NULL, **UNIQUE**              |
| city         | VARCHAR(60)  | NOT NULL                          |
| address      | VARCHAR(255) | NULL                              |
| capacity     | INT          | NOT NULL DEFAULT 0, `>= 0`        |

### 6. `products`
| Column      | Type          | Constraints                                   |
|-------------|---------------|-----------------------------------------------|
| product_id  | INT           | **PK**, AUTO_INCREMENT                        |
| sku         | VARCHAR(40)   | NOT NULL, **UNIQUE**                          |
| name        | VARCHAR(120)  | NOT NULL                                      |
| category_id | INT           | NOT NULL, **FK** → `categories.category_id`   |
| supplier_id | INT           | NOT NULL, **FK** → `suppliers.supplier_id`    |
| unit_price  | DECIMAL(10,2) | NOT NULL, `>= 0`                              |
| description | TEXT          | NULL                                          |
| created_at  | DATETIME      | NOT NULL DEFAULT CURRENT_TIMESTAMP            |

### 7. `stock`  *(resolves M:N products ↔ warehouses)*
| Column        | Type | Constraints                                                                |
|---------------|------|----------------------------------------------------------------------------|
| stock_id      | INT  | **PK**, AUTO_INCREMENT                                                     |
| product_id    | INT  | NOT NULL, **FK** → `products.product_id` (CASCADE)                         |
| warehouse_id  | INT  | NOT NULL, **FK** → `warehouses.warehouse_id` (CASCADE)                     |
| quantity      | INT  | NOT NULL DEFAULT 0, `>= 0`                                                 |
| reorder_level | INT  | NOT NULL DEFAULT 5, `>= 0`                                                 |
|               |      | **UNIQUE (product_id, warehouse_id)** so each product appears once per WH |

### 8. `customers`
| Column        | Type                            | Constraints                |
|---------------|---------------------------------|----------------------------|
| customer_id   | INT                             | **PK**, AUTO_INCREMENT     |
| full_name     | VARCHAR(100)                    | NOT NULL                   |
| email         | VARCHAR(120)                    | NOT NULL, **UNIQUE**       |
| phone         | VARCHAR(30)                     | NULL                       |
| address       | VARCHAR(255)                    | NULL                       |
| city          | VARCHAR(60)                     | NULL                       |
| customer_type | ENUM('retail','wholesale')      | NOT NULL DEFAULT 'retail'  |
| created_at    | DATETIME                        | NOT NULL DEFAULT NOW()     |

### 9. `orders`
| Column        | Type                                            | Constraints                                |
|---------------|-------------------------------------------------|--------------------------------------------|
| order_id      | INT                                             | **PK**, AUTO_INCREMENT                     |
| customer_id   | INT                                             | NOT NULL, **FK** → `customers.customer_id` |
| employee_id   | INT                                             | NOT NULL, **FK** → `employees.employee_id` |
| order_date    | DATETIME                                        | NOT NULL DEFAULT NOW()                     |
| status        | ENUM('pending','paid','shipped','cancelled')    | NOT NULL DEFAULT 'pending'                 |
| total_amount  | DECIMAL(12,2)                                   | NOT NULL DEFAULT 0, `>= 0`                 |

### 10. `order_items`  *(resolves M:N orders ↔ products)*
| Column        | Type          | Constraints                                              |
|---------------|---------------|----------------------------------------------------------|
| order_item_id | INT           | **PK**, AUTO_INCREMENT                                   |
| order_id      | INT           | NOT NULL, **FK** → `orders.order_id` (CASCADE)           |
| product_id    | INT           | NOT NULL, **FK** → `products.product_id`                 |
| quantity      | INT           | NOT NULL, `> 0`                                          |
| unit_price    | DECIMAL(10,2) | NOT NULL, `>= 0`                                         |
|               |               | **UNIQUE (order_id, product_id)** (each product appears once per order) |

---

## Normalisation argument (up to 3NF)

For every table:

- **1NF:** all attributes are atomic (no repeating groups, no list columns).
  M:N relationships are decomposed via `stock` and `order_items`.
- **2NF:** every non-key attribute depends on the *whole* primary key. All
  tables use surrogate single-column primary keys, so this is trivially
  satisfied; the natural composite keys (e.g. `(product_id, warehouse_id)`
  on `stock`) are enforced with `UNIQUE` constraints.
- **3NF:** no transitive dependencies.
    - Role information is factored out of `employees` into `roles`
      (otherwise `role_name`/`description` would depend on `role_id`,
      which depends on `employee_id`).
    - Category and supplier information is factored out of `products` into
      `categories` and `suppliers`.
    - Order line totals are NOT stored on `orders` per row but are summed
      from `order_items` (so `total_amount` is a derived/cached value
      maintained by the application layer when a line item is added or
      removed, to avoid update anomalies relative to the line items).

No multi-valued or transitive dependencies remain inside any single table.
