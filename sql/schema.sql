-- =====================================================================
-- Hardware Storage System - Database Schema
-- Database: hardware_storage
-- Normalization: Up to 3NF
-- =====================================================================

DROP DATABASE IF EXISTS hardware_storage;
CREATE DATABASE hardware_storage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hardware_storage;

-- ---------------------------------------------------------------------
-- 1) ROLES - lookup table for staff roles (3NF: separate role attributes)
-- ---------------------------------------------------------------------
CREATE TABLE roles (
    role_id       INT AUTO_INCREMENT PRIMARY KEY,
    role_name     VARCHAR(50) NOT NULL UNIQUE,
    description   VARCHAR(255) DEFAULT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2) EMPLOYEES - staff who log into the system
-- ---------------------------------------------------------------------
CREATE TABLE employees (
    employee_id   INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(120) NOT NULL UNIQUE,
    phone         VARCHAR(30)  DEFAULT NULL,
    role_id       INT          NOT NULL,
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    hired_on      DATE         NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT fk_emp_role FOREIGN KEY (role_id) REFERENCES roles(role_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3) CATEGORIES - product categories (CPU, GPU, RAM, Storage, etc.)
-- ---------------------------------------------------------------------
CREATE TABLE categories (
    category_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(80)  NOT NULL UNIQUE,
    description   VARCHAR(255) DEFAULT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4) SUPPLIERS - companies that supply hardware to the store
-- ---------------------------------------------------------------------
CREATE TABLE suppliers (
    supplier_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(120) NOT NULL UNIQUE,
    contact_name  VARCHAR(100) DEFAULT NULL,
    email         VARCHAR(120) DEFAULT NULL,
    phone         VARCHAR(30)  DEFAULT NULL,
    address       VARCHAR(255) DEFAULT NULL,
    country       VARCHAR(60)  DEFAULT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5) WAREHOUSES - physical storage locations
-- ---------------------------------------------------------------------
CREATE TABLE warehouses (
    warehouse_id  INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(80)  NOT NULL UNIQUE,
    city          VARCHAR(60)  NOT NULL,
    address       VARCHAR(255) DEFAULT NULL,
    capacity      INT          NOT NULL DEFAULT 0
        CHECK (capacity >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 6) PRODUCTS - hardware items
-- ---------------------------------------------------------------------
CREATE TABLE products (
    product_id    INT AUTO_INCREMENT PRIMARY KEY,
    sku           VARCHAR(40)  NOT NULL UNIQUE,
    name          VARCHAR(120) NOT NULL,
    category_id   INT          NOT NULL,
    supplier_id   INT          NOT NULL,
    unit_price    DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    description   TEXT         DEFAULT NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prod_cat FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_prod_sup FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 7) STOCK - per-warehouse stock levels (resolves M:N between products & warehouses)
-- ---------------------------------------------------------------------
CREATE TABLE stock (
    stock_id      INT AUTO_INCREMENT PRIMARY KEY,
    product_id    INT NOT NULL,
    warehouse_id  INT NOT NULL,
    quantity      INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_level INT NOT NULL DEFAULT 5 CHECK (reorder_level >= 0),
    UNIQUE KEY uk_product_warehouse (product_id, warehouse_id),
    CONSTRAINT fk_stock_prod FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_stock_wh   FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 8) CUSTOMERS - buyers
-- ---------------------------------------------------------------------
CREATE TABLE customers (
    customer_id   INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(120) NOT NULL UNIQUE,
    phone         VARCHAR(30)  DEFAULT NULL,
    address       VARCHAR(255) DEFAULT NULL,
    city          VARCHAR(60)  DEFAULT NULL,
    customer_type ENUM('retail','wholesale') NOT NULL DEFAULT 'retail',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 9) ORDERS - customer orders (header)
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    order_id      INT AUTO_INCREMENT PRIMARY KEY,
    customer_id   INT NOT NULL,
    employee_id   INT NOT NULL,
    order_date    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status        ENUM('pending','paid','shipped','cancelled') NOT NULL DEFAULT 'pending',
    total_amount  DECIMAL(12,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    CONSTRAINT fk_order_cust FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_order_emp  FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 10) ORDER_ITEMS - line items on each order (resolves M:N order<->product)
-- ---------------------------------------------------------------------
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id      INT NOT NULL,
    product_id    INT NOT NULL,
    quantity      INT NOT NULL CHECK (quantity > 0),
    unit_price    DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    UNIQUE KEY uk_order_product (order_id, product_id),
    CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_oi_prod  FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Helpful indexes
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_orders_customer   ON orders(customer_id);
CREATE INDEX idx_orders_employee   ON orders(employee_id);
CREATE INDEX idx_orderitems_order  ON order_items(order_id);
CREATE INDEX idx_orderitems_prod   ON order_items(product_id);
CREATE INDEX idx_stock_prod        ON stock(product_id);
CREATE INDEX idx_stock_warehouse   ON stock(warehouse_id);
