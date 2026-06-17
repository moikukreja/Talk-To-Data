"""
TalkToData engine — the exact three-phase NL-to-SQL contract from the notebook,
packaged for the FastAPI backend.

  Phase B : Google Gemini `gemini-2.0-flash` translates English -> SQLite SQL.
  Phase C : three guardrails gate every result; trusted_nl2sql() always returns
            a consistent dict with a `status` key.

Thread-safety (L6): FastAPI serves requests across threads, and an in-memory
SQLite DB is per-connection, so we open ONE connection with check_same_thread=
False and serialise access with a Lock. The DB is seeded once at import with
random.seed(42) for reproducibility — identical to the notebook.
"""
from __future__ import annotations

import os
import re
import random
import sqlite3
import threading
from datetime import date, timedelta

# --------------------------------------------------------------------------- DB
_DB_LOCK = threading.Lock()
_conn = sqlite3.connect(":memory:", check_same_thread=False)
_cur = _conn.cursor()


def _build_database() -> None:
    """Create + seed the five tables exactly as the case study specifies."""
    _cur.executescript(
        """
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
        """
    )

    random.seed(42)  # reproducibility — seed once, before any seeding
    cities = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Kolkata", "Pune", "Hyderabad"]
    cats = ["Skincare", "Haircare", "Electronics", "Wellness", "Fragrance"]

    for i in range(1, 61):
        _cur.execute(
            "INSERT INTO customers VALUES (?,?,?,?,?)",
            (i, f"Customer{i}", random.choice(cities),
             str(date(2025, 1, 1) + timedelta(days=random.randint(0, 400))),
             random.choice([0, 1])),
        )
    for i in range(1, 26):
        _cur.execute(
            "INSERT INTO products VALUES (?,?,?,?)",
            (i, f"Product{i}", random.choice(cats), round(random.uniform(199, 4999), 2)),
        )
    for i in range(1, 201):
        _cur.execute(
            "INSERT INTO orders VALUES (?,?,?,?,?)",
            (i, random.randint(1, 60),
             str(date(2026, 4, 1) + timedelta(days=random.randint(0, 70))),
             round(random.uniform(299, 9999), 2), random.choice(cities)),
        )
    for i in range(1, 401):
        _cur.execute(
            "INSERT INTO order_items VALUES (?,?,?,?)",
            (i, random.randint(1, 200), random.randint(1, 25), random.randint(1, 3)),
        )
    for i in range(1, 41):
        _cur.execute(
            "INSERT INTO returns VALUES (?,?,?,?)",
            (i, random.randint(1, 200),
             random.choice(["Damaged", "Wrong item", "Late", "Quality"]),
             str(date(2026, 4, 15) + timedelta(days=random.randint(0, 55)))),
        )
    _conn.commit()


_build_database()

# ----------------------------------------------------------------------- Phase B
SCHEMA = """
Tables:
customers(id, name, city, signup_date, is_repeat)
products(id, name, category, price)
orders(id, customer_id, order_date, total_amount, city)
order_items(id, order_id, product_id, quantity)
returns(id, order_id, reason, return_date)

Notes: is_repeat is 1 for repeat customers, 0 otherwise.
Dates are stored as TEXT in YYYY-MM-DD format.
"""

MODEL = "gemini-2.0-flash"  # Google Gemini, free tier (Google AI Studio)
_client = None  # lazily created so the module imports without a key present


def _get_client():
    global _client
    if _client is None:
        from google import genai  # lazy import; requires GEMINI_API_KEY in env
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        _client = genai.Client(api_key=api_key)
    return _client


def _extract_sql(text: str) -> str:
    """Robustly strip ```sql ... ``` fences / a leading 'sql' label (L5)."""
    s = text.strip()
    m = re.match(r"^```[a-zA-Z]*\s*(.*?)\s*```$", s, re.DOTALL)
    if m:
        s = m.group(1).strip()
    s = re.sub(r"^\s*sql\s*\n", "", s, flags=re.IGNORECASE)
    return s.strip()


def llm_nl2sql(question: str, schema: str = SCHEMA) -> str:
    prompt = f"""You are a translator from English to SQLite SQL.
Given this database schema:
{schema}
Translate this question into ONE valid SQLite query.
Return ONLY the SQL, no explanation, no markdown fences.

Question: {question}
SQL:"""
    resp = _get_client().models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    text = resp.text or ""
    return _extract_sql(text)


def run_sql(sql: str):
    """Execute a read query under the lock. Returns rows, or an error string."""
    try:
        with _DB_LOCK:
            _cur.execute(sql)
            return _cur.fetchall()
    except Exception as e:  # noqa: BLE001 — surface the DB error verbatim
        return f"SQL ERROR: {e}"


# ----------------------------------------------------------------------- Phase C
FORBIDDEN = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "REPLACE"]


def is_safe(sql: str) -> bool:
    """Guardrail 1 — block destructive ops on WHOLE-WORD match (L2)."""
    upper = sql.upper()
    return not any(re.search(r"\b" + w + r"\b", upper) for w in FORBIDDEN)


VALID_TABLES = {"customers", "products", "orders", "order_items", "returns"}


def references_only_real_tables(sql: str):
    """Guardrail 2 — validate FROM/JOIN/comma-join tables exist (L4)."""
    referenced: set[str] = set()
    pattern = r"\b(?:FROM|JOIN)\b\s+(.+?)(?=\b(?:WHERE|GROUP|ORDER|LIMIT|HAVING|JOIN|ON|UNION)\b|\)|;|$)"
    for clause in re.findall(pattern, sql, re.IGNORECASE | re.DOTALL):
        for part in clause.split(","):
            part = part.strip()
            if not part or part.startswith("("):  # skip subqueries
                continue
            name = re.split(r"\s+", part)[0].strip("`\"[]")
            if name:
                referenced.add(name.lower())
    unknown = referenced - VALID_TABLES
    return (len(unknown) == 0, unknown)


def guard(sql: str) -> dict:
    """Apply all three guardrails; always return a consistent status-keyed dict."""
    if not sql or not sql.strip():
        return {"status": "BLOCKED", "reason": "Empty SQL from model", "sql": sql}
    if not is_safe(sql):                                # Guardrail 1
        return {"status": "BLOCKED", "reason": "Dangerous operation", "sql": sql}
    ok, unknown = references_only_real_tables(sql)      # Guardrail 2
    if not ok:
        return {"status": "BLOCKED",
                "reason": f"Unknown table(s): {sorted(unknown)}", "sql": sql}
    # Guardrail 3: run, but ALWAYS return the SQL for human review
    return {"status": "OK", "sql": sql, "answer": run_sql(sql),
            "note": "Review the SQL above before trusting this number."}


def trusted_nl2sql(question: str) -> dict:
    """Translate with Gemini, then gate through the guardrails."""
    try:
        sql = llm_nl2sql(question)
    except Exception as e:  # noqa: BLE001 — e.g. missing key / network
        return {"status": "BLOCKED",
                "reason": f"Translation failed: {e}", "sql": ""}
    return guard(sql)
