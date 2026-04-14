# Import the libraries needed to create and populate the SQLite database for the store management system. This includes `sqlite3` for database operations, `random` for generating random data, and `datetime` for handling date-related functions. The script defines the database schema, populates it with sample data for suppliers, products, customers, and orders, and then sets up the database by executing the necessary SQL commands.
import sqlite3
import random
from datetime import date, timedelta
import re
from llama_index.llms.ollama import Ollama

DB_PATH = "store.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS suppliers (
    id            INTEGER PRIMARY KEY,
    name          TEXT,
    country       TEXT,
    lead_time_days INTEGER
);

CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY,
    name        TEXT,
    category    TEXT,
    price       REAL,
    stock       INTEGER,
    supplier_id INTEGER REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT,
    city        TEXT,
    joined_date TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER REFERENCES products(id),
    customer_id INTEGER REFERENCES customers(id),
    quantity    INTEGER,
    order_date  TEXT,
    status      TEXT
);
"""

suppliers = [
    (1, "AlphaSupply",   "Italy",   3),
    (2, "BetaGoods",     "Germany", 7),
    (3, "GammaTrade",    "China",  14),
    (4, "DeltaSource",   "USA",     5),
    (5, "EpsilonCo",     "France",  4),
]

products = [
    (1,  "Wireless Mouse",       "Electronics",  29.99,  120, 1),
    (2,  "Mechanical Keyboard",  "Electronics",  89.99,   45, 2),
    (3,  "USB-C Hub",            "Electronics",  39.99,    0, 3),
    (4,  "Standing Desk",        "Furniture",   349.99,   12, 4),
    (5,  "Ergonomic Chair",      "Furniture",   499.99,    8, 4),
    (6,  "Notebook A5",          "Stationery",    4.99,  500, 5),
    (7,  "Ballpoint Pens x10",   "Stationery",    6.99,  300, 5),
    (8,  "Monitor 27\"",         "Electronics", 299.99,   22, 2),
    (9,  "Laptop Stand",         "Accessories",  49.99,   60, 1),
    (10, "Webcam HD",            "Electronics",  79.99,    0, 3),
    (11, "Desk Lamp",            "Accessories",  34.99,   85, 5),
    (12, "Cable Organiser",      "Accessories",   9.99,  200, 1),
    (13, "Whiteboard 90x60",     "Furniture",    89.99,   15, 4),
    (14, "Sticky Notes Pack",    "Stationery",    3.49,  450, 5),
    (15, "Noise-Cancel Headset", "Electronics", 149.99,   18, 2),
]

cities = ["Milan", "Rome", "Turin", "Naples", "Florence",
          "Berlin", "Paris", "Madrid", "Amsterdam", "Vienna"]

random.seed(42)

def random_date(start_year=2022, end_year=2024):
    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    delta = (end - start).days
    return str(start + timedelta(days=random.randint(0, delta)))

customers = [
    (i, f"Customer_{i:03}", random.choice(cities), random_date(2021, 2023))
    for i in range(1, 51)
]

statuses = ["completed", "completed", "completed", "pending", "cancelled"]

orders = [
    (
        i,
        random.randint(1, 15),
        random.randint(1, 50),
        random.randint(1, 10),
        random_date(2023, 2024),
        random.choice(statuses),
    )
    for i in range(1, 201)
]

def setup():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(SCHEMA)
    cur.executemany("INSERT OR REPLACE INTO suppliers VALUES (?,?,?,?)", suppliers)
    cur.executemany("INSERT OR REPLACE INTO products  VALUES (?,?,?,?,?,?)", products)
    cur.executemany("INSERT OR REPLACE INTO customers VALUES (?,?,?,?)", customers)
    cur.executemany("INSERT OR REPLACE INTO orders    VALUES (?,?,?,?,?,?)", orders)
    con.commit()
    con.close()
    print(f"✅  store.db ready — {len(products)} products, {len(customers)} customers, {len(orders)} orders")

setup()

# Set up the Agent with the database connection and schema information. This allows the Agent to interact with the SQLite database, execute queries, and manage the store's data effectively. The `setup()` function initializes the database by creating the necessary tables and populating them with sample data for suppliers, products, customers, and orders.

DB_PATH = "store.db"

SCHEMA = """
suppliers(id, name, country, lead_time_days)
products(id, name, category, price, stock, supplier_id)
customers(id, name, city, joined_date)
orders(id, product_id, customer_id, quantity, order_date, status)
status values: 'completed', 'pending', 'cancelled'
"""

PROMPT = f"""You are a SQLite expert. Write ONE valid SQLite SELECT query for the question.
Return ONLY the SQL, no explanation, no markdown.

RULES:
- Return ONLY the raw SQL query, nothing else — no markdown, no explanation
- Never use INSERT, UPDATE, DELETE or DROP
- Use JOINs when data from multiple tables is needed

Schema:
{SCHEMA}

Question: """

llm = Ollama(model="gemma4:e2b", request_timeout=300.0)


def get_sql(question):
    response = llm.complete(PROMPT + question)
    sql = str(response).strip()
    
    # remove markdown fences if the model added them
    match = re.search(r"```(?:sql)?\s*(.*?)```", sql, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
    
    return sql


def run_sql(sql):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows


def ask(question):
    print(f"\nQuestion: {question}")
    
    sql = get_sql(question)
    print(f"SQL: {sql}")
    
    try:
        rows = run_sql(sql)
        print(f"Results: {len(rows)} rows")
        for row in rows:
            print(" ", row)
    except Exception as e:
        print(f"Error: {e}")


# run it
questions = [
    "Which supplier has the longest lead time?",
    "What is the average order quantity per product category?",
]

for q in questions:
    ask(q)