-- ============================================================
-- Retail Analytics Dashboard — SQLite Schema
-- ============================================================

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id  TEXT PRIMARY KEY,
    first_name   TEXT,
    last_name    TEXT,
    email        TEXT,
    state        TEXT,
    city         TEXT,
    segment      TEXT,       -- Premium / Regular / Budget
    join_date    DATE,
    age          INTEGER
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT,
    category     TEXT,
    subcategory  TEXT,
    price        REAL,
    cost         REAL
);

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   TEXT PRIMARY KEY,
    customer_id      TEXT,
    product_id       TEXT,
    quantity         INTEGER,
    store_id         TEXT,
    channel          TEXT,       -- Online / In-Store / Mobile App
    transaction_date DATE,
    discount_pct     REAL,
    unit_price       REAL,
    revenue          REAL,
    cogs             REAL,
    gross_profit     REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);
