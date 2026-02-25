# data/seed_database.py
import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker()
random.seed(42)
Faker.seed(42)

DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.sqlite")

# --- Schema ---
SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id   INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE,
    country       TEXT,
    signup_date   DATE
);

CREATE TABLE IF NOT EXISTS products (
    product_id    INTEGER PRIMARY KEY,
    product_name  TEXT NOT NULL,
    category      TEXT,
    unit_price    REAL,
    stock_qty     INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    order_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER REFERENCES customers(customer_id),
    order_date    DATE,
    status        TEXT CHECK(status IN ('completed','pending','cancelled','refunded'))
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id       INTEGER PRIMARY KEY,
    order_id      INTEGER REFERENCES orders(order_id),
    product_id    INTEGER REFERENCES products(product_id),
    quantity      INTEGER,
    unit_price    REAL
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id     INTEGER PRIMARY KEY,
    product_id    INTEGER REFERENCES products(product_id),
    customer_id   INTEGER REFERENCES customers(customer_id),
    rating        INTEGER CHECK(rating BETWEEN 1 AND 5),
    review_date   DATE
);
"""

CATEGORIES = ["Electronics", "Clothing", "Home & Kitchen", "Sports", "Books", "Beauty", "Toys"]
STATUSES = ["completed", "pending", "cancelled", "refunded"]
STATUS_WEIGHTS = [0.70, 0.15, 0.10, 0.05]
COUNTRIES = ["Singapore", "Malaysia", "Indonesia", "Thailand", "Philippines", "Vietnam", "Australia"]

def random_date(start_days_ago=730, end_days_ago=0):
    days = random.randint(end_days_ago, start_days_ago)
    return (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")

def seed(conn):
    cur = conn.cursor()

    # Customers (500)
    customers = []
    for i in range(1, 501):
        customers.append((i, fake.name(), fake.unique.email(),
                          random.choice(COUNTRIES), random_date(1000, 200)))
    cur.executemany("INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?)", customers)

    # Products (80)
    products = []
    for i in range(1, 81):
        products.append((i, fake.catch_phrase(), random.choice(CATEGORIES),
                         round(random.uniform(5.0, 800.0), 2),
                         random.randint(0, 500)))
    cur.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)", products)

    # Orders (3,000)
    orders = []
    for i in range(1, 3001):
        orders.append((i, random.randint(1, 500), random_date(730, 0),
                       random.choices(STATUSES, STATUS_WEIGHTS)[0]))
    cur.executemany("INSERT OR IGNORE INTO orders VALUES (?,?,?,?)", orders)

    # Order items (1–4 items per order)
    items = []
    item_id = 1
    for order_id in range(1, 3001):
        for _ in range(random.randint(1, 4)):
            product_id = random.randint(1, 80)
            qty = random.randint(1, 5)
            price = round(random.uniform(5.0, 800.0), 2)
            items.append((item_id, order_id, product_id, qty, price))
            item_id += 1
    cur.executemany("INSERT OR IGNORE INTO order_items VALUES (?,?,?,?,?)", items)

    # Reviews (1,500)
    reviews = []
    for i in range(1, 1501):
        reviews.append((i, random.randint(1, 80), random.randint(1, 500),
                        random.randint(1, 5), random_date(700, 0)))
    cur.executemany("INSERT OR IGNORE INTO reviews VALUES (?,?,?,?,?)", reviews)

    conn.commit()
    print("✅ Database seeded successfully!")
    print(f"   → Customers: 500 | Products: 80 | Orders: 3,000 | Reviews: 1,500")
    print(f"   → Saved to: {DB_PATH}")

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    seed(conn)
    conn.close()