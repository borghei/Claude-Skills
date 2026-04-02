-- schema.sql — Sample e-commerce DDL for the schema explorer
--
-- This schema defines 6 tables for a SaaS e-commerce platform.
-- Use with the sql-database-assistant skill's schema explorer
-- and query analyzer tools.

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(150) NOT NULL,
    phone           VARCHAR(20),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMP,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    role            VARCHAR(20) NOT NULL DEFAULT 'customer'
);

CREATE TABLE products (
    id              SERIAL PRIMARY KEY,
    sku             VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    price_cents     INTEGER NOT NULL CHECK (price_cents >= 0),
    currency        VARCHAR(3) NOT NULL DEFAULT 'USD',
    category        VARCHAR(100),
    stock_quantity  INTEGER NOT NULL DEFAULT 0,
    is_published    BOOLEAN NOT NULL DEFAULT FALSE,
    weight_grams    INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_sku ON products(sku);

CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    status          VARCHAR(30) NOT NULL DEFAULT 'pending',
    subtotal_cents  INTEGER NOT NULL,
    tax_cents       INTEGER NOT NULL DEFAULT 0,
    shipping_cents  INTEGER NOT NULL DEFAULT 0,
    total_cents     INTEGER NOT NULL,
    shipping_address TEXT,
    billing_address  TEXT,
    notes           TEXT,
    placed_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    shipped_at      TIMESTAMP,
    delivered_at    TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);

CREATE TABLE order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL,
    total_cents     INTEGER NOT NULL
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);

CREATE TABLE reviews (
    id              SERIAL PRIMARY KEY,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    user_id         INTEGER NOT NULL REFERENCES users(id),
    rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title           VARCHAR(200),
    body            TEXT,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Note: no index on reviews.product_id or reviews.user_id (design issue)

CREATE TABLE inventory_log (
    id              SERIAL PRIMARY KEY,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    change_qty      INTEGER NOT NULL,
    reason          VARCHAR(50) NOT NULL,
    reference_id    INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by      INTEGER REFERENCES users(id)
);

-- Note: no index on inventory_log.product_id (design issue for frequent lookups)
