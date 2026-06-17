# Phase 1 verification script — Step 0 (DB) + Phase A (rule-based).
# Run locally to confirm the notebook cells produce correct, reproducible output
# BEFORE embedding them into the Colab notebook (Deliverable 2).

import sqlite3, random
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# STEP 0 — Build the in-memory SQLite database (exactly as the case study specs)
# ---------------------------------------------------------------------------
conn = sqlite3.connect(':memory:')   # database lives in memory
cur = conn.cursor()

cur.executescript('''
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT,
                        signup_date TEXT, is_repeat INTEGER);
CREATE TABLE products  (id INTEGER PRIMARY KEY, name TEXT, category TEXT,
                        price REAL);
CREATE TABLE orders    (id INTEGER PRIMARY KEY, customer_id INTEGER,
                        order_date TEXT, total_amount REAL, city TEXT);
CREATE TABLE order_items(id INTEGER PRIMARY KEY, order_id INTEGER,
                        product_id INTEGER, quantity INTEGER);
CREATE TABLE returns   (id INTEGER PRIMARY KEY, order_id INTEGER,
                        reason TEXT, return_date TEXT);
''')
print('Tables created.')

# L1 FIX: seed RNG ONCE, before any data generation, for full reproducibility.
random.seed(42)

cities = ['Mumbai','Delhi','Bengaluru','Chennai','Kolkata','Pune','Hyderabad']
cats   = ['Skincare','Haircare','Electronics','Wellness','Fragrance']

# 60 customers
for i in range(1, 61):
    cur.execute('INSERT INTO customers VALUES (?,?,?,?,?)',
                (i, f'Customer{i}', random.choice(cities),
                 str(date(2025,1,1)+timedelta(days=random.randint(0,400))),
                 random.choice([0,1])))

# 25 products
for i in range(1, 26):
    cur.execute('INSERT INTO products VALUES (?,?,?,?)',
                (i, f'Product{i}', random.choice(cats), round(random.uniform(199,4999),2)))

# 200 orders
for i in range(1, 201):
    cur.execute('INSERT INTO orders VALUES (?,?,?,?,?)',
                (i, random.randint(1,60),
                 str(date(2026,4,1)+timedelta(days=random.randint(0,70))),
                 round(random.uniform(299,9999),2), random.choice(cities)))

# 400 order items
for i in range(1, 401):
    cur.execute('INSERT INTO order_items VALUES (?,?,?,?)',
                (i, random.randint(1,200), random.randint(1,25), random.randint(1,3)))

# 40 returns
for i in range(1, 41):
    cur.execute('INSERT INTO returns VALUES (?,?,?,?)',
                (i, random.randint(1,200),
                 random.choice(['Damaged','Wrong item','Late','Quality']),
                 str(date(2026,4,15)+timedelta(days=random.randint(0,55)))))

conn.commit()
print('Data seeded.')

# Verify the DB is real with a hand-written query
cur.execute('SELECT COUNT(*) FROM orders')
print('Total orders:', cur.fetchone()[0])

# Extra reproducibility probes (so we know the seeded numbers)
cur.execute("SELECT COUNT(*) FROM orders WHERE LOWER(city)='mumbai'")
print('Mumbai orders (seed=42):', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM customers'); print('Customers:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM products');  print('Products:', cur.fetchone()[0])

# ---------------------------------------------------------------------------
# PHASE A — Rule-based NL-to-SQL (hand-written keyword rules; no ML, no LLM)
# ---------------------------------------------------------------------------
def rule_based_nl2sql(question):
    q = question.lower()

    # Rule 1: counting orders, optionally by city
    if 'how many orders' in q:
        for city in ['mumbai','delhi','bengaluru','chennai','kolkata','pune','hyderabad']:
            if city in q:
                return (f"SELECT COUNT(*) FROM orders "
                        f"WHERE LOWER(city)='{city}'")
        return 'SELECT COUNT(*) FROM orders'

    # Rule 2: total revenue
    if 'total revenue' in q or 'how much' in q and 'sold' in q:
        return 'SELECT SUM(total_amount) FROM orders'

    # Rule 3: number of customers
    if 'how many customers' in q:
        return 'SELECT COUNT(*) FROM customers'

    return None  # no rule matched  (NOTE: returns None, never raises)

# PREDICT: Q1 -> Mumbai count; Q2 -> SAME query (last week IGNORED, silently wrong);
#          Q3 -> None (needs a join+grouping no rule anticipates).
for question in [
    'How many orders came from Mumbai?',
    'How many orders did we get from Mumbai last week?',
    'Which product category earns the most revenue?',
]:
    print(question)
    print('   ->', rule_based_nl2sql(question))
    print()

# Prove the "returns None, not an exception" contract on totally unseen input
print('Unseen phrasing ->', rule_based_nl2sql('Show me the meaning of life'))
