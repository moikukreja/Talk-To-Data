# Phase 3 verification: all three guardrails + trusted_nl2sql's consistent dict.
# Fully deterministic (no LLM) -> these are the REAL outputs embedded in the notebook.
import sqlite3, random, re, json
from datetime import date, timedelta

# rebuild the exact seeded DB
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

def run_sql(sql):
    try:
        cur.execute(sql); return cur.fetchall()
    except Exception as e:
        return f'SQL ERROR: {e}'

# --- Guardrail 1: block dangerous ops (L2: word boundaries) ----------------
FORBIDDEN = ['DROP','DELETE','UPDATE','INSERT','ALTER','TRUNCATE','REPLACE']
def is_safe(sql):
    upper = sql.upper()
    return not any(re.search(r'\b' + w + r'\b', upper) for w in FORBIDDEN)

# --- Guardrail 2: validate referenced tables exist (L4: FROM+JOIN+commas) ---
VALID_TABLES = {'customers','products','orders','order_items','returns'}
def references_only_real_tables(sql):
    referenced = set()
    pattern = r'\b(?:FROM|JOIN)\b\s+(.+?)(?=\b(?:WHERE|GROUP|ORDER|LIMIT|HAVING|JOIN|ON|UNION)\b|\)|;|$)'
    for clause in re.findall(pattern, sql, re.IGNORECASE | re.DOTALL):
        for part in clause.split(','):
            part = part.strip()
            if not part or part.startswith('('):      # skip subqueries
                continue
            name = re.split(r'\s+', part)[0].strip('`"[]')
            if name:
                referenced.add(name.lower())
    unknown = referenced - VALID_TABLES
    return (len(unknown) == 0, unknown)

# --- Guardrail 3 + consistent dict (shared by trusted_nl2sql and the demo) --
def _guard(sql):
    if not sql or not sql.strip():
        return {'status': 'BLOCKED', 'reason': 'Empty SQL from model', 'sql': sql}
    if not is_safe(sql):                                   # Guardrail 1
        return {'status': 'BLOCKED', 'reason': 'Dangerous operation', 'sql': sql}
    ok, unknown = references_only_real_tables(sql)         # Guardrail 2
    if not ok:
        return {'status': 'BLOCKED', 'reason': f'Unknown table(s): {sorted(unknown)}', 'sql': sql}
    return {'status': 'OK', 'sql': sql, 'answer': run_sql(sql),   # Guardrail 3: always return sql
            'note': 'Review the SQL above before trusting this number.'}

# trusted_nl2sql(question) = _guard(llm_nl2sql(question)); we exercise _guard directly here.

print("=== Guardrail 1 (is_safe) ===")
for s, exp in [('SELECT COUNT(*) FROM orders', True), ('DROP TABLE orders', False),
               ('DELETE FROM customers', False), ("SELECT updated_at FROM orders", True),
               ("SELECT * FROM returns", True)]:
    got = is_safe(s)
    print(("PASS" if got == exp else "FAIL"), f"is_safe({s!r}) = {got}")

print("\n=== Guardrail 2 (references_only_real_tables) ===")
for s in ['SELECT COUNT(*) FROM orders',
          'SELECT p.category FROM order_items oi JOIN products p ON oi.product_id=p.id GROUP BY p.category',
          'SELECT * FROM orders o, customers c WHERE o.customer_id=c.id',
          'SELECT * FROM nonexistent_table',
          'SELECT * FROM orders JOIN ghost g ON g.id=orders.id']:
    print(references_only_real_tables(s), "<-", s)

print("\n=== trusted_nl2sql consistent dict — all three cases ===")
print("OK case:")
print(json.dumps(_guard("SELECT COUNT(*) FROM orders WHERE LOWER(city)='mumbai'"), indent=2))
print("\nBLOCKED (dangerous):")
print(json.dumps(_guard("DROP TABLE orders"), indent=2))
print("\nBLOCKED (unknown table):")
print(json.dumps(_guard("SELECT * FROM secret_admin_table"), indent=2))
