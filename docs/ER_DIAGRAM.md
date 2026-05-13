# ER Diagram

Entity-Relationship diagram for the Hardware Storage System.
Rendered with [Mermaid](https://mermaid.js.org/) — GitHub renders this
natively, or you can paste it into <https://mermaid.live>.

```mermaid
erDiagram
    ROLES ||--o{ EMPLOYEES : "is held by"
    EMPLOYEES ||--o{ ORDERS : "processes"
    CUSTOMERS ||--o{ ORDERS : "places"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "appears on"
    CATEGORIES ||--o{ PRODUCTS : "classifies"
    SUPPLIERS ||--o{ PRODUCTS : "supplies"
    PRODUCTS ||--o{ STOCK : "has stock of"
    WAREHOUSES ||--o{ STOCK : "stores"

    ROLES {
        INT role_id PK
        VARCHAR role_name "UNIQUE"
        VARCHAR description
    }
    EMPLOYEES {
        INT employee_id PK
        VARCHAR username "UNIQUE"
        VARCHAR password_hash
        VARCHAR full_name
        VARCHAR email "UNIQUE"
        VARCHAR phone
        INT role_id FK
        TINYINT is_active
        DATE hired_on
    }
    CATEGORIES {
        INT category_id PK
        VARCHAR name "UNIQUE"
        VARCHAR description
    }
    SUPPLIERS {
        INT supplier_id PK
        VARCHAR name "UNIQUE"
        VARCHAR contact_name
        VARCHAR email
        VARCHAR phone
        VARCHAR address
        VARCHAR country
    }
    WAREHOUSES {
        INT warehouse_id PK
        VARCHAR name "UNIQUE"
        VARCHAR city
        VARCHAR address
        INT capacity
    }
    PRODUCTS {
        INT product_id PK
        VARCHAR sku "UNIQUE"
        VARCHAR name
        INT category_id FK
        INT supplier_id FK
        DECIMAL unit_price
        TEXT description
        DATETIME created_at
    }
    STOCK {
        INT stock_id PK
        INT product_id FK
        INT warehouse_id FK
        INT quantity
        INT reorder_level
    }
    CUSTOMERS {
        INT customer_id PK
        VARCHAR full_name
        VARCHAR email "UNIQUE"
        VARCHAR phone
        VARCHAR address
        VARCHAR city
        ENUM customer_type "retail | wholesale"
        DATETIME created_at
    }
    ORDERS {
        INT order_id PK
        INT customer_id FK
        INT employee_id FK
        DATETIME order_date
        ENUM status "pending | paid | shipped | cancelled"
        DECIMAL total_amount
    }
    ORDER_ITEMS {
        INT order_item_id PK
        INT order_id FK
        INT product_id FK
        INT quantity
        DECIMAL unit_price
    }
```

## Cardinalities

- A **role** is held by zero-or-more **employees**.
- An **employee** processes zero-or-more **orders**.
- A **customer** places zero-or-more **orders**.
- An **order** contains one-or-more **order items**.
- A **product** can appear on zero-or-more **order items**.
- A **category** classifies zero-or-more **products**.
- A **supplier** supplies zero-or-more **products**.
- A **product** can be stocked in zero-or-more **warehouses** (via `stock`),
  and a **warehouse** can store zero-or-more **products** (M:N resolved by the
  `stock` table).

## Notes on resolving M:N relationships

Two many-to-many relationships exist in the domain and are each resolved by
an associative (junction) table:

| Many-to-many                | Resolved by   |
|-----------------------------|---------------|
| products  ↔  warehouses     | `stock`       |
| orders    ↔  products       | `order_items` |
