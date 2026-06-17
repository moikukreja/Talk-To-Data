# Phase 2 verification: prove the deterministic plumbing (SQL fence-stripper +
# run_sql) works, and compute the TRUE answers from the seed=42 DB so the
# notebook's illustrative Phase B outputs carry real numbers (not fabricated).
import sqlite3, random, re
from datetime import date, timedelta

# --- rebuild the exact seeded DB (same as Phase 1) -------------------------
conn = sqlite3.connect(':memory:'); cur = conn.cursor()
cur.executescript('''
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT, signup_date TEXT, is_repeat INTEGER);
CREATE TABLE products  (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders    (id INTEGER PRIMARY KEY, customer_id INTEGER, order_date TEXT, total_amount REAL, city TEXT);
CREATE TABLE order_items(id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER);
CREATE TABLE returns   (id INTEGER PRIMARY KEY, order_id INTEGER, reason TEXT, return_date TEXT);
''')
random.seed(42)
cities = ['Mumbai','Delhi','Bengaluru','Chennai','Kolkata','Pune','Hyderabad']
cats   = ['Skincare','Haircare','Electronics','Wellness','Fragrance']
for i in range(1,61):
    cur.execute('INSERT INTO customers VALUES (?,?,?,?,?)',(i,f'Customer{i}',random.choice(cities),
        str(date(2025,1,1)+timedelta(days=random.randint(0,400))),random.choice([0,1])))
for i in range(1,26):
    cur.execute('INSERT INTO products VALUES (?,?,?,?)',(i,f'Product{i}',random.choice(cats),round(random.uniform(199,4999),2)))
for i in range(1,201):
    cur.execute('INSERT INTO orders VALUES (?,?,?,?,?)',(i,random.randint(1,60),
        str(date(2026,4,1)+timedelta(days=random.randint(0,70))),round(random.uniform(299,9999),2),random.choice(cities)))
for i in range(1,401):
    cur.execute('INSERT INTO order_items VALUES (?,?,?,?)',(i,random.randint(1,200),random.randint(1,25),random.randint(1,3)))
for i in range(1,41):
    cur.execute('INSERT INTO returns VALUES (?,?,?,?)',(i,random.randint(1,200),
        random.choice(['Damaged','Wrong item','Late','Quality']),str(date(2026,4,15)+timedelta(days=random.randint(0,55)))))
conn.commit()

# --- the robust SQL extractor (L5 fix) -------------------------------------
def _extract_sql(text):
    s = text.strip()
    m = re.match(r'^```[a-zA-Z]*\s*(.*?)\s*```$', s, re.DOTALL)   # strip ```sql ... ``` fences
    if m:
        s = m.group(1).strip()
    s = re.sub(r'^\s*sql\s*\n', '', s, flags=re.IGNORECASE)       # strip a leading 'sql' label line
    return s.strip()

def run_sql(sql):
    try:
        cur.execute(sql); return cur.fetchall()
    except Exception as e:
        return f'SQL ERROR: {e}'

# --- TEST 1: extractor handles fenced / labelled / clean variants ----------
cases = {
    "```sql\nSELECT COUNT(*) FROM orders\n```": "SELECT COUNT(*) FROM orders",
    "```\nSELECT 1\n```":                       "SELECT 1",
    "sql\nSELECT 2":                            "SELECT 2",
    "SELECT 3":                                 "SELECT 3",
    "  SELECT 4  ":                             "SELECT 4",
}
print("=== Extractor tests ===")
for raw, want in cases.items():
    got = _extract_sql(raw)
    print(("PASS" if got == want else f"FAIL got={got!r}"), "<-", repr(raw))

# --- TEST 2: true answers for the demo questions (seed=42) -----------------
print("\n=== True answers (seed=42) for illustrative notebook outputs ===")
q2 = ("SELECT p.category, SUM(oi.quantity * p.price) AS revenue "
      "FROM order_items oi JOIN products p ON oi.product_id = p.id "
      "GROUP BY p.category ORDER BY revenue DESC LIMIT 1")
print("Q2 top category :", run_sql(q2))

q3_correct = ("SELECT AVG(o.total_amount) FROM orders o "
              "JOIN customers c ON o.customer_id = c.id WHERE c.is_repeat = 1")
print("Q3 CORRECT (repeat-only avg):", run_sql(q3_correct))

q3_wrong = "SELECT AVG(total_amount) FROM orders"
print("Q3 WRONG  (all-orders avg)  :", run_sql(q3_wrong))

# extractor on a guardrail-relevant fenced dangerous query (used in Phase C)
print("\nExtractor on fenced DROP:", _extract_sql("```sql\nDROP TABLE orders\n```"))
