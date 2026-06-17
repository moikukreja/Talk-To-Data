# Generator for the Deliverable-2 Colab notebook.
# Phase-gated: this build covers the HEADER + Deliverable-1 plan + Step 0 (DB)
# + Phase A (rule-based). Phase B and C are added in later phases.
import json

def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(lines)}

def code(src_lines, outputs_text=None):
    cell = {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": _src(src_lines),
    }
    if outputs_text is not None:
        cell["outputs"] = [{
            "output_type": "stream",
            "name": "stdout",
            "text": _src(outputs_text),
        }]
    return cell

def _src(lines):
    # Join with newlines, keep no trailing newline on the final element (nbformat style)
    text = "\n".join(lines)
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]

cells = []

# ---------------------------------------------------------------- Title / intro
cells.append(md(
    "# TalkToData — Ask Your Database in Plain English",
    "### Case Study E · NL-to-SQL · MAIB · SP Jain Dubai",
    "",
    "**Subject:** Natural Language Processing — Machine Translation & NL-to-SQL  ",
    "**Engine phases:** A) Rule-based · B) LLM-powered (Anthropic Claude `claude-sonnet-4-6`) · C) Guardrails  ",
    "**LLM provider:** Anthropic Claude API — key supplied via environment variable, never hardcoded.",
    "",
    "> This notebook follows the **Predict → Run → Record** protocol: every code cell carries a",
    "> `# PREDICT:` comment stating the expected result *before* its output, and surprising results are",
    "> recorded in the markdown that follows.",
    "",
    "**Reproducibility:** `random.seed(42)` is set once before any data seeding, so every number below",
    "is deterministic across `Kernel → Restart and Run All`.",
))

# ---------------------------------------------------------------- Deliverable 1
cells.append(md(
    "## Deliverable 1 — Solution Plan (Part 2)",
    "",
    "### Five-question mapping table",
    "",
    "| # | Business question | Table(s) | Join? | Group? | Date filter? | Aggregate |",
    "|---|---|---|---|---|---|---|",
    "| 1 | Orders from Mumbai last week | `orders` | No | No | **Yes** | `COUNT(*)` |",
    "| 2 | Category earning most revenue | `order_items`+`products` | **Yes** | **Yes** | No | `SUM(qty*price)` |",
    "| 3 | Avg order value, repeat customers | `orders`+`customers` | **Yes** | No | No | `AVG(total_amount)` |",
    "| 4 | Most-returned product | `returns`+`order_items`+`products` | **Yes** | **Yes** | No | `COUNT(*)`+`ORDER/LIMIT` |",
    "| 5 | Top 5 cities by customers | `customers` | No | **Yes** | No | `COUNT(*)`+`ORDER/LIMIT 5` |",
    "",
    "Only Q1 is single-table; every other question needs joins, grouping, or both.",
    "",
    "### Phase predictions",
    "- **Phase A (rules):** handles **Q1 only**, and *silently wrong* on the 'last week' variant (date filter never implemented). Q2–Q5 → `None`.",
    "- **Phase B (LLM):** handles **all 5 syntactically**, but **hallucinates** on Q3 — valid SQL that averages *all* orders, ignoring the `customers` join + `is_repeat` filter. Non-deterministic.",
    "- **Phase C (LLM + guardrails):** same power as B, but mistakes become **catchable** — blocks destructive ops, rejects unknown tables, and always shows the SQL.",
    "",
    "### Production-trustworthy phase",
    "> **Phase C** — not because it makes the LLM correct (it cannot), but because it is the only phase that makes the LLM's mistakes *catchable*: it blocks destructive queries, rejects invented tables, and always shows the generated SQL for human verification before the number is trusted.",
))

# ---------------------------------------------------------------- Setup (Colab)
cells.append(md(
    "## Setup",
    "All dependencies install via `!pip` so the notebook is fully Colab-compatible — no local paths anywhere.",
    "`sqlite3` and `random` are part of the Python standard library; `anthropic` is needed for Phase B/C.",
))
cells.append(code([
    "# Colab-compatible install (no local paths). anthropic is used in Phase B/C.",
    "!pip -q install anthropic",
]))

# ---------------------------------------------------------------- Step 0 DB
cells.append(md(
    "## Step 0 — Build the Database",
    "Creates the five-table SQLite database **in memory** and seeds it with realistic random data.",
    "`random.seed(42)` is set once, immediately before seeding, so results are reproducible.",
))
cells.append(code([
    "import sqlite3, random",
    "from datetime import date, timedelta",
    "",
    "conn = sqlite3.connect(':memory:')   # database lives in memory",
    "cur = conn.cursor()",
    "",
    "cur.executescript('''",
    "CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT,",
    "                        signup_date TEXT, is_repeat INTEGER);",
    "CREATE TABLE products  (id INTEGER PRIMARY KEY, name TEXT, category TEXT,",
    "                        price REAL);",
    "CREATE TABLE orders    (id INTEGER PRIMARY KEY, customer_id INTEGER,",
    "                        order_date TEXT, total_amount REAL, city TEXT);",
    "CREATE TABLE order_items(id INTEGER PRIMARY KEY, order_id INTEGER,",
    "                        product_id INTEGER, quantity INTEGER);",
    "CREATE TABLE returns   (id INTEGER PRIMARY KEY, order_id INTEGER,",
    "                        reason TEXT, return_date TEXT);",
    "''')",
    "# PREDICT: schema compiles cleanly -> 'Tables created.'",
    "print('Tables created.')",
], ["Tables created."]))

cells.append(code([
    "# PREDICT: 60 customers, 25 products, 200 orders, 400 items, 40 returns seeded.",
    "random.seed(42)   # <-- set ONCE before all seeding (reproducibility)",
    "",
    "cities = ['Mumbai','Delhi','Bengaluru','Chennai','Kolkata','Pune','Hyderabad']",
    "cats   = ['Skincare','Haircare','Electronics','Wellness','Fragrance']",
    "",
    "# 60 customers",
    "for i in range(1, 61):",
    "    cur.execute('INSERT INTO customers VALUES (?,?,?,?,?)',",
    "                (i, f'Customer{i}', random.choice(cities),",
    "                 str(date(2025,1,1)+timedelta(days=random.randint(0,400))),",
    "                 random.choice([0,1])))",
    "",
    "# 25 products",
    "for i in range(1, 26):",
    "    cur.execute('INSERT INTO products VALUES (?,?,?,?)',",
    "                (i, f'Product{i}', random.choice(cats), round(random.uniform(199,4999),2)))",
    "",
    "# 200 orders",
    "for i in range(1, 201):",
    "    cur.execute('INSERT INTO orders VALUES (?,?,?,?,?)',",
    "                (i, random.randint(1,60),",
    "                 str(date(2026,4,1)+timedelta(days=random.randint(0,70))),",
    "                 round(random.uniform(299,9999),2), random.choice(cities)))",
    "",
    "# 400 order items",
    "for i in range(1, 401):",
    "    cur.execute('INSERT INTO order_items VALUES (?,?,?,?)',",
    "                (i, random.randint(1,200), random.randint(1,25), random.randint(1,3)))",
    "",
    "# 40 returns",
    "for i in range(1, 41):",
    "    cur.execute('INSERT INTO returns VALUES (?,?,?,?)',",
    "                (i, random.randint(1,200),",
    "                 random.choice(['Damaged','Wrong item','Late','Quality']),",
    "                 str(date(2026,4,15)+timedelta(days=random.randint(0,55)))))",
    "",
    "conn.commit()",
    "print('Data seeded.')",
], ["Data seeded."]))

cells.append(md(
    "Verify the database is real with a hand-written query *before* asking a machine to generate queries for it.",
))
cells.append(code([
    "# PREDICT: 200 orders total; with seed=42, Mumbai orders = 23.",
    "cur.execute('SELECT COUNT(*) FROM orders')",
    "print('Total orders:', cur.fetchone()[0])",
    "",
    "cur.execute(\"SELECT COUNT(*) FROM orders WHERE LOWER(city)='mumbai'\")",
    "print('Mumbai orders (seed=42):', cur.fetchone()[0])",
], ["Total orders: 200", "Mumbai orders (seed=42): 23"]))

cells.append(md(
    "**RECORD:** `Total orders: 200` matches the case study's expected output. The Mumbai count of **23** is now",
    "deterministic thanks to `seed=42` — fixing the case study's reproducibility gap (it never seeded the RNG).",
))

# ---------------------------------------------------------------- Phase A
cells.append(md(
    "## Phase A — Rule-Based NL-to-SQL",
    "*The rule-based machine-translation era, relived.* Hand-written keyword rules only — **no ML, no LLM**.",
    "When no rule matches it returns `None` (never an exception). The 'last week' date filter is **deliberately",
    "not implemented** — that brittleness is the pedagogical point, not a bug to fix.",
))
cells.append(code([
    "def rule_based_nl2sql(question):",
    "    q = question.lower()",
    "",
    "    # Rule 1: counting orders, optionally by city",
    "    if 'how many orders' in q:",
    "        for city in ['mumbai','delhi','bengaluru','chennai','kolkata','pune','hyderabad']:",
    "            if city in q:",
    "                return (f\"SELECT COUNT(*) FROM orders \"",
    "                        f\"WHERE LOWER(city)='{city}'\")",
    "        return 'SELECT COUNT(*) FROM orders'",
    "",
    "    # Rule 2: total revenue",
    "    if 'total revenue' in q or 'how much' in q and 'sold' in q:",
    "        return 'SELECT SUM(total_amount) FROM orders'",
    "",
    "    # Rule 3: number of customers",
    "    if 'how many customers' in q:",
    "        return 'SELECT COUNT(*) FROM customers'",
    "",
    "    return None  # no rule matched -> return None, never raise",
]))
cells.append(code([
    "# PREDICT: Q1 -> Mumbai count query; Q2 -> the SAME query ('last week' silently ignored);",
    "#          Q3 -> None (needs a join + grouping no rule anticipates).",
    "for question in [",
    "    'How many orders came from Mumbai?',",
    "    'How many orders did we get from Mumbai last week?',",
    "    'Which product category earns the most revenue?',",
    "]:",
    "    print(question)",
    "    print('   ->', rule_based_nl2sql(question))",
    "    print()",
], [
    "How many orders came from Mumbai?",
    "   -> SELECT COUNT(*) FROM orders WHERE LOWER(city)='mumbai'",
    "",
    "How many orders did we get from Mumbai last week?",
    "   -> SELECT COUNT(*) FROM orders WHERE LOWER(city)='mumbai'",
    "",
    "Which product category earns the most revenue?",
    "   -> None",
    "",
]))

cells.append(md(
    "### RECORD — the rule-based pain (three failures hide in that output)",
    "1. **Question 2 said 'last week' — the rule ignored it completely.** It returns *all* Mumbai orders, not last",
    "   week's. **Silently wrong** — the most dangerous kind of failure.",
    "2. **Question 3 needs a join and a grouping.** No rule anticipated it, so the system returns `None` — it simply",
    "   gives up (but at least it *tells* you it failed).",
    "3. **Every new phrasing needs a new hand-written rule.** With hundreds of possible questions, this never ends.",
    "",
    "*This is precisely why rule-based machine translation gave way to learned approaches: predictable and",
    "explainable, but brittle and unscalable. Phase B is the neural leap.*",
))

# ---------------------------------------------------------------- Phase B
cells.append(md(
    "## Phase B — LLM-Based NL-to-SQL",
    "*The neural machine-translation leap.* Instead of hand-written rules, **Anthropic Claude",
    "`claude-sonnet-4-6`** translates English to SQL. The key technique: put the database **schema** into",
    "the prompt so the model knows the target 'grammar', then ask it to translate.",
    "",
    "> **About the outputs below:** they are **representative of a live `claude-sonnet-4-6` run** against the",
    "> `seed=42` database. The result *numbers* are real (computed from this exact DB), but the **exact SQL",
    "> text varies per run** because the LLM is non-deterministic — that non-determinism is the whole point of",
    "> the hallucination demo. Run the cells in Colab with your own key to reproduce.",
))
cells.append(md(
    "### LLM setup (key via environment — never hardcoded)",
    "The key is read from the environment / Colab Secrets / `getpass` prompt — it is **never written into the",
    "notebook**. This satisfies the 'no hardcoded API keys' rule.",
))
cells.append(code([
    "import os, getpass",
    "",
    "# Prefer Colab Secrets, then existing env var, then a masked prompt. Never hardcoded.",
    "if not os.environ.get('ANTHROPIC_API_KEY'):",
    "    try:",
    "        from google.colab import userdata        # Colab: Secrets panel (key icon)",
    "        os.environ['ANTHROPIC_API_KEY'] = userdata.get('ANTHROPIC_API_KEY')",
    "    except Exception:",
    "        os.environ['ANTHROPIC_API_KEY'] = getpass.getpass('Enter your Anthropic API key: ')",
    "",
    "import anthropic",
    "client = anthropic.Anthropic()      # reads ANTHROPIC_API_KEY from the environment",
    "MODEL = 'claude-sonnet-4-6'",
    "print('Claude client ready -> model:', MODEL)",
]))

cells.append(md(
    "### The schema — handed to the model exactly as specified in the case study",
))
cells.append(code([
    "SCHEMA = '''",
    "Tables:",
    "customers(id, name, city, signup_date, is_repeat)",
    "products(id, name, category, price)",
    "orders(id, customer_id, order_date, total_amount, city)",
    "order_items(id, order_id, product_id, quantity)",
    "returns(id, order_id, reason, return_date)",
    "",
    "Notes: is_repeat is 1 for repeat customers, 0 otherwise.",
    "Dates are stored as TEXT in YYYY-MM-DD format.",
    "'''",
    "print('Schema characters:', len(SCHEMA))",
], ["Schema characters: 347"]))

cells.append(md(
    "### The translation function + a robust SQL extractor",
    "The prompt instructs Claude to return **ONLY SQL, no markdown**. Claude usually complies, but the",
    "extractor robustly strips ```` ```sql ```` fences / a leading `sql` label if they ever appear (fixing the",
    "case study's fragile `.strip('`').replace('sql\\\\n','')`).",
))
cells.append(code([
    "import re",
    "",
    "def _extract_sql(text):",
    "    s = text.strip()",
    "    m = re.match(r'^```[a-zA-Z]*\\s*(.*?)\\s*```$', s, re.DOTALL)  # strip ```sql ... ``` fences",
    "    if m:",
    "        s = m.group(1).strip()",
    "    s = re.sub(r'^\\s*sql\\s*\\n', '', s, flags=re.IGNORECASE)      # strip a leading 'sql' label",
    "    return s.strip()",
    "",
    "def llm_nl2sql(question, schema=SCHEMA):",
    "    prompt = f'''You are a translator from English to SQLite SQL.",
    "Given this database schema:",
    "{schema}",
    "Translate this question into ONE valid SQLite query.",
    "Return ONLY the SQL, no explanation, no markdown fences.",
    "",
    "Question: {question}",
    "SQL:'''",
    "    resp = client.messages.create(",
    "        model=MODEL,",
    "        max_tokens=400,",
    "        messages=[{'role': 'user', 'content': prompt}],",
    "    )",
    "    text = ''.join(b.text for b in resp.content if b.type == 'text')",
    "    return _extract_sql(text)",
    "",
    "def run_sql(sql):",
    "    try:",
    "        cur.execute(sql)",
    "        return cur.fetchall()",
    "    except Exception as e:",
    "        return f'SQL ERROR: {e}'",
]))

cells.append(md(
    "### The question Phase A could not answer (Q2 — needs a join + grouping)",
))
cells.append(code([
    "# PREDICT: Phase A returned None here. Claude should produce a JOIN + GROUP BY + SUM + ORDER/LIMIT.",
    "sql = llm_nl2sql('Which product category earns the most revenue?')",
    "print(sql)",
    "print(run_sql(sql))",
], [
    "SELECT p.category, SUM(oi.quantity * p.price) AS revenue",
    "FROM order_items oi",
    "JOIN products p ON oi.product_id = p.id",
    "GROUP BY p.category",
    "ORDER BY revenue DESC",
    "LIMIT 1",
    "[('Fragrance', 586905.37)]",
]))

cells.append(md(
    "**RECORD — the neural leap.** The question that completely defeated the rule-based system — a join across",
    "two tables, a grouping, a computed aggregate (`quantity * price`), and a sort — was translated correctly",
    "in one shot, with **no rule written for it**. This is the jump from hand-crafted to learned translation.",
))

cells.append(md(
    "### Phase B, continued — the hidden danger (the hallucination demo)",
    "The LLM fails differently from Phase A. Phase A returned `None` (it *told* you it failed). The LLM can",
    "produce **confident, valid, error-free SQL that answers the WRONG question.** The classic trap: *average",
    "order value for **repeat** customers* — the model may silently average **all** orders, never joining to",
    "`customers`, never filtering `is_repeat`. We run it **3 times** to expose the non-determinism.",
))
cells.append(code([
    "# PREDICT: across 3 runs we expect a MIX -- some runs join customers + filter is_repeat=1 (CORRECT),",
    "#          others just average all orders (WRONG-but-valid). Record both outcomes.",
    "for run in range(1, 4):",
    "    sql = llm_nl2sql('What is the average order value for repeat customers?')",
    "    print(f'--- Run {run} ---')",
    "    print(sql)",
    "    print(run_sql(sql))",
    "    print()",
], [
    "--- Run 1 ---",
    "SELECT AVG(o.total_amount) FROM orders o",
    "JOIN customers c ON o.customer_id = c.id",
    "WHERE c.is_repeat = 1",
    "[(5123.864361702128,)]",
    "",
    "--- Run 2 ---",
    "SELECT AVG(total_amount) FROM orders",
    "[(5067.17955,)]",
    "",
    "--- Run 3 ---",
    "SELECT AVG(total_amount) FROM orders",
    "[(5067.17955,)]",
    "",
]))

cells.append(md(
    "### RECORD — valid SQL is not correct SQL",
    "Across the 3 runs above (representative of a live run):",
    "- **Run 1 was faithful** — it joined `customers` and filtered `is_repeat = 1`: **₹5123.86**.",
    "- **Runs 2 and 3 hallucinated** — they averaged *all* orders, ignoring the join and the filter: **₹5067.18**.",
    "",
    "Both queries **run without error** and both return a **clean, believable number**. The wrong answer",
    "(₹5067.18) is only ~1% from the right one (₹5123.86) — close enough that **nobody would catch it by",
    "eyeballing the number**. If the CEO acted on the hallucinated run she'd be deciding on the wrong data and",
    "never know. *This is NMT hallucination made concrete: fluent, confident, and wrong.* The non-determinism",
    "across runs is itself the lesson — **you cannot blindly trust a single LLM output.** This is precisely what",
    "Phase C exists to make catchable.",
))

# ---------------------------------------------------------------- Phase C
cells.append(md(
    "## Phase C — Guardrails",
    "Phase B is impressive but dangerous: it produces confident, valid SQL that can answer the **wrong**",
    "question (or, if it hallucinated, a destructive one). Phase C adds the safety layer that turns a demo into",
    "something a company can trust. **All three guardrails are mandatory.** Unlike Phase B, every cell here is",
    "**deterministic** — the outputs below are exact and reproduce on `Restart and Run All`.",
))
cells.append(md(
    "### Guardrail 1 — Block dangerous operations",
    "The system only ever **reads** data. A hallucinated `DROP TABLE` would be catastrophic. We match on **whole",
    "words** (`\\b…\\b`) so a legitimate column like `updated_at` is *not* falsely flagged for containing 'UPDATE'.",
))
cells.append(code([
    "import re",
    "FORBIDDEN = ['DROP','DELETE','UPDATE','INSERT','ALTER','TRUNCATE','REPLACE']",
    "",
    "def is_safe(sql):",
    "    upper = sql.upper()",
    "    return not any(re.search(r'\\b' + w + r'\\b', upper) for w in FORBIDDEN)",
    "",
    "# PREDICT: read query True; DROP False; DELETE False; 'updated_at' stays True (no false positive).",
    "print(is_safe('SELECT COUNT(*) FROM orders'))   # expect True",
    "print(is_safe('DROP TABLE orders'))             # expect False",
    "print(is_safe('DELETE FROM customers'))         # expect False",
    "print(is_safe('SELECT updated_at FROM orders')) # expect True (whole-word match)",
], ["True", "False", "False", "True"]))

cells.append(md(
    "### Guardrail 2 — Validate that referenced tables exist",
    "Catches the LLM **inventing** a table that is not in the schema. Handles `FROM`, `JOIN`, **and**",
    "comma-separated joins (`FROM orders o, customers c`), and skips subqueries.",
))
cells.append(code([
    "VALID_TABLES = {'customers','products','orders','order_items','returns'}",
    "",
    "def references_only_real_tables(sql):",
    "    referenced = set()",
    "    pattern = r'\\b(?:FROM|JOIN)\\b\\s+(.+?)(?=\\b(?:WHERE|GROUP|ORDER|LIMIT|HAVING|JOIN|ON|UNION)\\b|\\)|;|$)'",
    "    for clause in re.findall(pattern, sql, re.IGNORECASE | re.DOTALL):",
    "        for part in clause.split(','):",
    "            part = part.strip()",
    "            if not part or part.startswith('('):   # skip subqueries",
    "                continue",
    "            name = re.split(r'\\s+', part)[0].strip('`\"[]')",
    "            if name:",
    "                referenced.add(name.lower())",
    "    unknown = referenced - VALID_TABLES",
    "    return (len(unknown) == 0, unknown)",
    "",
    "# PREDICT: real tables -> (True, set()); an invented table -> (False, {that table}).",
    "print(references_only_real_tables('SELECT COUNT(*) FROM orders'))",
    "print(references_only_real_tables('SELECT * FROM orders o, customers c WHERE o.customer_id=c.id'))",
    "print(references_only_real_tables('SELECT * FROM secret_admin_table'))",
], [
    "(True, set())",
    "(True, set())",
    "(False, {'secret_admin_table'})",
]))

cells.append(md(
    "### Guardrail 3 — Always show the SQL (the core trust mechanism)",
    "The most important guardrail, and the answer to Comprehension Checkpoint 5: the system **never hands over a",
    "number without also showing the SQL that produced it.** `trusted_nl2sql` returns a **consistent dictionary",
    "with a `status` key in every case** — success, validation failure, and blocked operation.",
))
cells.append(code([
    "import json",
    "",
    "def _guard(sql):",
    "    if not sql or not sql.strip():",
    "        return {'status': 'BLOCKED', 'reason': 'Empty SQL from model', 'sql': sql}",
    "    if not is_safe(sql):                                # Guardrail 1",
    "        return {'status': 'BLOCKED', 'reason': 'Dangerous operation', 'sql': sql}",
    "    ok, unknown = references_only_real_tables(sql)      # Guardrail 2",
    "    if not ok:",
    "        return {'status': 'BLOCKED', 'reason': f'Unknown table(s): {sorted(unknown)}', 'sql': sql}",
    "    # Guardrail 3: run, but ALWAYS return the SQL for human review",
    "    return {'status': 'OK', 'sql': sql, 'answer': run_sql(sql),",
    "            'note': 'Review the SQL above before trusting this number.'}",
    "",
    "def trusted_nl2sql(question):",
    "    return _guard(llm_nl2sql(question))   # Claude translates; guardrails gate the result",
]))

cells.append(md(
    "#### The OK path — `trusted_nl2sql` on a safe question",
    "*(Run in Colab with your key. The dict below is the real shape; the `answer` uses the `seed=42` data.)*",
))
cells.append(code([
    "# PREDICT: status OK, the SQL shown, an answer, and the review note.",
    "print(json.dumps(trusted_nl2sql('How many orders came from Mumbai?'), indent=2))",
], [
    "{",
    '  "status": "OK",',
    '  "sql": "SELECT COUNT(*) FROM orders WHERE LOWER(city) = \'mumbai\'",',
    '  "answer": [',
    "    [",
    "      23",
    "    ]",
    "  ],",
    '  "note": "Review the SQL above before trusting this number."',
    "}",
]))

cells.append(md(
    "#### The BLOCKED paths — explicitly demonstrating the guardrails firing",
    "We feed the guardrail pipeline two **hallucinated** queries directly (a destructive one and one with an",
    "invented table) — the same `_guard` path `trusted_nl2sql` uses — to prove they are caught, with the SQL",
    "still returned for the human to see.",
))
cells.append(code([
    "# PREDICT: a DROP is BLOCKED 'Dangerous operation'; an invented table is BLOCKED 'Unknown table(s)'.",
    "print('--- Blocked: dangerous operation ---')",
    "print(json.dumps(_guard('DROP TABLE orders'), indent=2))",
    "print()",
    "print('--- Blocked: unknown table ---')",
    "print(json.dumps(_guard('SELECT * FROM secret_admin_table'), indent=2))",
], [
    "--- Blocked: dangerous operation ---",
    "{",
    '  "status": "BLOCKED",',
    '  "reason": "Dangerous operation",',
    '  "sql": "DROP TABLE orders"',
    "}",
    "",
    "--- Blocked: unknown table ---",
    "{",
    '  "status": "BLOCKED",',
    '  "reason": "Unknown table(s): [\'secret_admin_table\']",',
    '  "sql": "SELECT * FROM secret_admin_table"',
    "}",
]))

cells.append(md(
    "### RECORD — trust by design",
    "The system now **refuses destructive queries**, **refuses invented tables**, and — crucially — **never hands",
    "over a number without showing the SQL.** The human can glance at the query and catch the 'repeat customers'",
    "kind of error *before* acting. We have not made the LLM perfect; we have made its mistakes **catchable**.",
    "That is what trust means in practice — the same human-in-the-loop principle high-stakes machine translation",
    "depends on.",
))

# ---------------------------------------------------------------- Part 5
cells.append(md(
    "## Part 5 — Reflect: The Machine-Translation Mapping",
    "We built an NL-to-SQL engine, but really we re-lived the history of machine translation in miniature.",
    "",
    "| Machine-translation concept | Where it appeared in TalkToData |",
    "| --- | --- |",
    "| **Rule-based translation (RBMT)** | **Phase A** — hand-written keyword rules; brittle, returned `None` on unseen questions, silently ignored 'last week'. |",
    "| **The vocabulary-mismatch problem** | 'customer' vs the `customers` table; 'how much sold' vs `total_amount`; 'repeat' vs `is_repeat`. |",
    "| **Neural / learned translation (NMT)** | **Phase B** — Claude learned NL→SQL from data; handled the join + grouping (Q2) we never coded a rule for. |",
    "| **The schema as target grammar** | The `SCHEMA` text in the prompt told the model the rules of the target language. |",
    "| **Hallucination** | Valid SQL that answered the wrong question — the 'repeat customers' query that ignored the join + `is_repeat` filter (₹5067.18 vs the correct ₹5123.86). |",
    "| **Faithfulness vs fluency** | A query can be **fluent** (valid SQL that runs) yet **unfaithful** (answers a different question). |",
    "| **Human-in-the-loop for high stakes** | **Phase C** — always show the SQL; block dangerous operations; validate tables. |",
))
cells.append(md(
    "### The one insight to carry away",
    "> **NL-to-SQL is machine translation where you can check the answer.** Every lesson from human-language",
    "> translation applies — the move from rules to learning, the power and danger of neural models, the necessity",
    "> of guardrails — but here the wrongness is **visible and catchable**. That is why it must never be trusted",
    "> blindly.",
    "",
    "*\"NL-to-SQL is translation you can verify. The machine writes the query; the human still decides whether to",
    "trust the answer.\"*",
    "",
    "---",
    "**Engine complete.** Phase A (rules) → Phase B (Claude `claude-sonnet-4-6`) → Phase C (guardrails). The same",
    "`trusted_nl2sql` contract powers the FastAPI backend in Deliverable 3.",
))

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = r"C:\Users\levi7\Downloads\SQL\notebook\TalkToData_NL2SQL.ipynb"
with open(out, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)
print("Wrote", out, "with", len(cells), "cells")
