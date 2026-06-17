**CASE STUDY E**

**TalkToData**

_Ask Your Database in Plain English — An NL-to-SQL Case Study_

MAIB | Natural Language Processing | Machine Translation & NL-to-SQL

**How This Case Study Works**

This case study has five parts, and they are deliberately ordered. You do not start with code. You start by understanding the problem, then planning your solution, and only then building it. Each part unlocks the next.

| **Part** | **What you do** | **What you produce** |
| --- | --- | --- |
| 1\. Understand | Read the business case; answer comprehension checkpoints | Written answers, in your own words |
| 2\. Plan | Map questions to data; predict where each approach wins and fails | A one-page solution plan |
| 3\. Build | Execute the three phases, one cell at a time | A working NL-to-SQL engine |
| 4\. Ship | Wrap it in a UI | An 'ask your database' app |
| 5\. Reflect | Map what you built back to machine translation | A trust memo |

<div class="joplin-table-wrapper"><table><tbody><tr><td><p><strong>The Predict → Run → Record protocol (Parts 3 onward)</strong></p><p>For every code cell in the build phases:</p><ul><li>PREDICT — before running, write one comment line: what do you expect?</li><li>RUN — execute and read the actual output.</li><li>RECORD — if it surprised you, note why. The surprises are the lesson.</li></ul></td></tr></tbody></table></div>

**PART 1 — Understand the Problem**

**Your Role**

You are the founding engineer at TalkToData, a young startup building an analytics layer for fast-growing Indian consumer brands. Your first client is a direct-to-consumer brand — think of a Mamaearth or a boAt — selling personal-care and electronics products online across India.

The brand is doing well, which is exactly the problem. Every day, decisions need numbers. The marketing head wants to know which city is buying the most. The category manager wants to know which product gets returned most often. The CEO wants yesterday's revenue before her 9 AM call. None of these people write SQL. So every question becomes a ticket in a queue, handled by a two-person data team who are now forty requests behind. Decisions that should take minutes take days.

**The CEO's ask**

_"I want to ask my database questions in plain English and get the answer back. 'How many orders came from Mumbai last week?' — and I get a number, in seconds, not a three-day wait for the data team. I don't want to learn SQL. And I need to trust the answer."_

**Why This Matters — The Significance**

What the CEO is describing has a name in the industry: natural-language-to-SQL, or NL-to-SQL. It is one of the hottest areas in enterprise software right now, and understanding why will sharpen how you think about the whole project.

**It is data democratization**

In most companies, the people who have the business questions (managers, founders, marketers) are not the people who can query the database (analysts, engineers). This gap is a bottleneck on every decision. NL-to-SQL removes the gap — anyone who can type a question can get an answer. Microsoft has built it into Power BI as Copilot. Google has it in Looker. Startups like Seek AI and Text2SQL are funded specifically to solve it. Every business-intelligence tool on the market is racing to add it.

**It is machine translation — with a twist**

This is the conceptual heart of the case study, and the reason it follows our machine translation session. NL-to-SQL is translation: you translate from a source language (English) into a target language (SQL). It has every challenge of human-language translation — ambiguity, vocabulary mismatch, different structure — but with one enormous advantage:

**The twist that makes NL-to-SQL special**

_In human translation, a wrong output just sounds slightly off — hard to detect automatically. In NL-to-SQL, a wrong translation either throws an error or returns visibly wrong numbers. The output is verifiable. This makes NL-to-SQL the safest possible place to learn one of the most important lessons in modern AI: how machines translate, where they fail, and how to catch them when they do._

**The bottleneck it breaks is real money**

A data team answering forty queries by hand is forty decisions delayed. In a fast-moving consumer brand, a delayed decision about which product to restock or which city to target is lost revenue. The value of TalkToData is not the technology — it is the collapse of a three-day wait into three seconds, multiplied across every manager in the company, every day.

**Comprehension Checkpoints**

Before you go any further, answer these in your own words in a document or markdown cell. Do not write code. Do not skip ahead. These questions check that you understand the problem you are about to solve — and the answers will shape every design decision you make later.

1.  In one or two sentences, explain the actual bottleneck at the client company. It is not 'they have no software' — describe the real human gap that NL-to-SQL closes.
2.  Write down three different English questions a manager might ask that all mean the same thing — for example, three ways to ask for the number of orders from Mumbai. Why does this variety make a simple keyword-matching system fragile?
3.  NL-to-SQL was described as a kind of machine translation. Name the 'source language' and the 'target language'. What plays the role of grammar that the translation must obey?
4.  The case study claims a wrong SQL query is easier to catch than a wrong French sentence. Explain why in your own words. What are the two ways a wrong SQL query reveals itself?
5.  The CEO said 'I need to trust the answer.' What might 'trust' require beyond just returning a number? Think about what you would want to see before you acted on a number a machine gave you.

**Why this gate exists**

_Question 5 is the entire project in disguise. If you can articulate now what 'trust' requires, you will understand by the end why Phase C (guardrails) and the 'show the SQL' verification view are not optional extras — they are the point. Hold on to your answer; you will return to it._

**PART 2 — Plan the Solution**

A plan comes before code. Engineers who skip planning end up with code that works on the first example and collapses on the second. This part produces a one-page plan that you submit before you build. Still no programming — just understanding the data and predicting what will happen.

**The Database You Will Work With**

TalkToData connects to the client's e-commerce database. It has five tables. You do not need to memorise them, but you must understand how they relate — because every question the CEO asks will require pulling from one or more of these, often joined together.

| **Table** | **What it holds** | **Key columns** |
| --- | --- | --- |
| customers | One row per customer | id, name, city, signup_date, is_repeat |
| products | One row per product sold | id, name, category, price |
| orders | One row per order placed | id, customer_id, order_date, total_amount, city |
| order_items | Line items within orders | id, order_id, product_id, quantity |
| returns | One row per returned order | id, order_id, reason, return_date |

The relationships (this is the 'grammar' your translation must respect):

- An order belongs to a customer (orders.customer_id points to customers.id)
- An order contains one or more items (order_items.order_id points to orders.id)
- Each item refers to a product (order_items.product_id points to products.id)
- A return refers to an order (returns.order_id points to orders.id)

**The vocabulary-mismatch problem — sound familiar?**

_The CEO says 'customer.' The schema says 'customers.' She says 'how much we sold' — the schema says 'total_amount.' She says 'returns' — meaning the returns table, not the SQL keyword RETURN. This is exactly the vocabulary mismatch from machine translation: the source language and the target language do not use the same words for the same things. Your system's job is to bridge that gap._

**Map Five Questions to the Data**

Here are five questions the CEO might ask. For each one, before writing any code, fill in a planning table: which tables are needed, whether a join is required, and whether it needs grouping, a date filter, or an aggregate (COUNT, SUM, AVG). Do this on paper or in a cell. This is the core of your plan.

| **Business question** | **Think about...** |
| --- | --- |
| How many orders came from Mumbai last week? | one table? date filter? a count? |
| Which product category earns us the most revenue? | a join? grouping? a sum? |
| What is the average order value for repeat customers? | a join to customers? a filter on is_repeat? an average? |
| Which product gets returned most often? | two or three tables joined? grouping? ordering? |
| List the top 5 cities by number of customers. | grouping? counting? sorting? a limit? |

_Notice as you fill this in: only the first question is answerable from a single table with a simple filter. The rest need joins, grouping, or both. Keep that observation — it is about to become the whole story._

**Predict Where Each Approach Will Win and Fail**

You will build the system three ways, in three phases. Before you build anything, predict how each will perform. Write your predictions down — you will check them against reality at the end.

| **Approach** | **Predict: which of the 5 questions will it handle? Where will it break?** |
| --- | --- |
| Phase A — Rule-based (hand-written keyword rules) | Your prediction: \____ |
| Phase B — LLM-based (schema in the prompt) | Your prediction: \____ |
| Phase C — LLM + guardrails | Your prediction: \____ |

<div class="joplin-table-wrapper"><table><tbody><tr><td><p><strong>Your Part 2 deliverable</strong></p><p>Before moving to Part 3, produce a one-page plan containing:</p><ul><li>Your completed five-question mapping table</li><li>Your three predictions for the three phases</li><li>One sentence: based on your plan, which phase do you expect the client will actually be able to trust in production, and why?</li></ul></td></tr></tbody></table></div>

**PART 3 — Build the Engine**

Now you build, one cell at a time, in three phases. The phases deliberately retrace the history of machine translation you learned this session: hand-written rules first, then a learned model, then safety guardrails. You will feel why each era gave way to the next.

**Step 0 — Build the Database**

Run this once. It creates the SQLite database in memory and fills it with sample data. SQLite is built into Python — nothing to install, nothing to download. Read the code; you are building the five tables from your plan.

import sqlite3, random

from datetime import date, timedelta

conn = sqlite3.connect(':memory:') # database lives in memory

cur = conn.cursor()

cur.executescript('''

CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT,

signup_date TEXT, is_repeat INTEGER);

CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT,

price REAL);

CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER,

order_date TEXT, total_amount REAL, city TEXT);

CREATE TABLE order_items(id INTEGER PRIMARY KEY, order_id INTEGER,

product_id INTEGER, quantity INTEGER);

CREATE TABLE returns (id INTEGER PRIMARY KEY, order_id INTEGER,

reason TEXT, return_date TEXT);

''')

print('Tables created.')

Now seed it with sample data. The numbers are random but realistic — enough that queries return believable answers.

cities = \['Mumbai','Delhi','Bengaluru','Chennai','Kolkata','Pune','Hyderabad'\]

cats = \['Skincare','Haircare','Electronics','Wellness','Fragrance'\]

\# 60 customers

for i in range(1, 61):

cur.execute('INSERT INTO customers VALUES (?,?,?,?,?)',

(i, f'Customer{i}', random.choice(cities),

str(date(2025,1,1)+timedelta(days=random.randint(0,400))),

random.choice(\[0,1\])))

\# 25 products

for i in range(1, 26):

cur.execute('INSERT INTO products VALUES (?,?,?,?)',

(i, f'Product{i}', random.choice(cats), round(random.uniform(199,4999),2)))

\# 200 orders

for i in range(1, 201):

cur.execute('INSERT INTO orders VALUES (?,?,?,?,?)',

(i, random.randint(1,60),

str(date(2026,4,1)+timedelta(days=random.randint(0,70))),

round(random.uniform(299,9999),2), random.choice(cities)))

\# order items + returns

for i in range(1, 401):

cur.execute('INSERT INTO order_items VALUES (?,?,?,?)',

(i, random.randint(1,200), random.randint(1,25), random.randint(1,3)))

for i in range(1, 41):

cur.execute('INSERT INTO returns VALUES (?,?,?,?)',

(i, random.randint(1,200), random.choice(\['Damaged','Wrong item','Late','Quality'\]),

str(date(2026,4,15)+timedelta(days=random.randint(0,55)))))

conn.commit()

print('Data seeded.')

Verify it works with a hand-written query, so you know the database is real before you try to generate queries for it:

cur.execute('SELECT COUNT(\*) FROM orders')

print('Total orders:', cur.fetchone()\[0\])

**Expected output:**

Total orders: 200

**Phase A — Rule-Based NL-to-SQL**

**Why this phase exists**

This is the rule-based machine translation era, relived. Before statistics and neural networks, translation meant humans hand-writing rules. You will do exactly that for NL-to-SQL: write rules that spot keywords in the question and assemble SQL from them. It will work — for the questions you anticipated — and break the moment a user phrases something you did not foresee. Feeling that brittleness firsthand is the point.

Build a small rule-based translator. It looks for keywords and stitches together a query:

def rule_based_nl2sql(question):

q = question.lower()

\# Rule 1: counting orders, optionally by city

if 'how many orders' in q:

for city in \['mumbai','delhi','bengaluru','chennai','kolkata','pune','hyderabad'\]:

if city in q:

return (f"SELECT COUNT(\*) FROM orders "

f"WHERE LOWER(city)='{city}'")

return 'SELECT COUNT(\*) FROM orders'

\# Rule 2: total revenue

if 'total revenue' in q or 'how much' in q and 'sold' in q:

return 'SELECT SUM(total_amount) FROM orders'

\# Rule 3: number of customers

if 'how many customers' in q:

return 'SELECT COUNT(\*) FROM customers'

return None # no rule matched

**PREDICT: which of these three questions will get a correct query, and which will return None?**

\# My predictions: \____

for question in \[

'How many orders came from Mumbai?',

'How many orders did we get from Mumbai last week?',

'Which product category earns the most revenue?',

\]:

print(question)

print(' ->', rule_based_nl2sql(question))

print()

**Expected output:**

How many orders came from Mumbai?

\-> SELECT COUNT(\*) FROM orders WHERE LOWER(city)='mumbai'

How many orders did we get from Mumbai last week?

\-> SELECT COUNT(\*) FROM orders WHERE LOWER(city)='mumbai'

Which product category earns the most revenue?

\-> None

<div class="joplin-table-wrapper"><table><tbody><tr><td><p><strong>What just happened — the rule-based pain</strong></p><p>Three failures hide in this output, and you should record all three:</p><ul><li>Question 2 said 'last week' — the rule ignored it completely. It returns ALL Mumbai orders, not last week's. Silently wrong.</li><li>Question 3 needs a join and a grouping. No rule anticipated it. Returns None — the system simply gives up.</li><li>Every new phrasing needs a new hand-written rule. With hundreds of possible questions, this never ends.</li></ul></td></tr></tbody></table></div>

_This is precisely why rule-based machine translation gave way to learned approaches. Hand-written rules are predictable and explainable, but brittle and unscalable. You have now felt that tradeoff in your own code._

**Phase B — LLM-Based NL-to-SQL**

**Why this phase exists**

This is the neural machine translation leap. Instead of you hand-writing rules, a large language model — which has learned the mapping between English and SQL from enormous amounts of data — does the translation. The key technique is simple and powerful: you put the database schema into the prompt, so the model knows what tables and columns exist, then ask it to translate the question into SQL.

First, describe your schema as text. This is what you hand the model so it knows the 'grammar' of the target language:

SCHEMA = '''

Tables:

customers(id, name, city, signup_date, is_repeat)

products(id, name, category, price)

orders(id, customer_id, order_date, total_amount, city)

order_items(id, order_id, product_id, quantity)

returns(id, order_id, reason, return_date)

Notes: is_repeat is 1 for repeat customers, 0 otherwise.

Dates are stored as TEXT in YYYY-MM-DD format.

'''

Now the translation function. This uses an LLM through whatever API you have access to. The example uses a generic chat-completion call — adapt the client line to your provider (OpenAI, Anthropic, Gemini, or a free Hugging Face model). What matters is the PROMPT, not the provider.

\# Adapt this import + client to whichever LLM you can access.

\# The technique is identical regardless of provider.

def llm_nl2sql(question, schema=SCHEMA):

prompt = f'''You are a translator from English to SQLite SQL.

Given this database schema:

{schema}

Translate this question into ONE valid SQLite query.

Return ONLY the SQL, no explanation, no markdown fences.

Question: {question}

SQL:'''

response = call_your_llm(prompt) # <- your provider's call here

sql = response.strip().strip('\`').replace('sql\\n', '')

return sql

**PREDICT: the same question 3 that returned None in Phase A. Will the LLM produce a working query with a join and grouping?**

\# My prediction: \____

sql = llm_nl2sql('Which product category earns the most revenue?')

print(sql)

**Expected output (the exact SQL will vary, but it should look like):**

SELECT p.category, SUM(oi.quantity \* p.price) AS revenue

FROM order_items oi

JOIN products p ON oi.product_id = p.id

GROUP BY p.category

ORDER BY revenue DESC

LIMIT 1

Run it against the real database and get the answer:

def run_sql(sql):

try:

cur.execute(sql)

return cur.fetchall()

except Exception as e:

return f'SQL ERROR: {e}'

print(run_sql(sql))

**Expected output:**

\[('Electronics', 287653.4)\] # your category and number will differ

**What just happened — the neural leap**

_The question that completely defeated your rule-based system — needing a join across two tables, a grouping, an aggregate, and a sort — was translated correctly by the LLM in one shot. You wrote no rule for it. The model learned how to write SQL from data, exactly as neural machine translation learned to translate from data. This is your own Google-2016 moment: the jump from hand-crafted to learned._

**Phase B, continued — The Hidden Danger**

The LLM is impressive. It is also dangerous in a way the rule-based system never was. The rule-based system, when it failed, returned None — it told you it failed. The LLM fails differently: it produces confident, fluent, perfectly-valid SQL that answers the WRONG question. This is the hallucination problem from neural machine translation, made concrete.

Try this question, which contains a subtle trap:

\# My prediction: \____

sql = llm_nl2sql('What is the average order value for repeat customers?')

print(sql)

print(run_sql(sql))

**The model may produce something that looks like this — and runs without any error:**

SELECT AVG(total_amount) FROM orders

\[(5123.45,)\] # a clean number, no error

**Valid SQL is not correct SQL**

_Look carefully. The question asked for repeat customers only. But this query averages ALL orders — it never joined to the customers table, never filtered on is_repeat. It runs perfectly. It returns a clean, believable number. And it answers a different question than the one asked. If the CEO acted on this, she would be making a decision on the wrong data and would never know. This is exactly NMT hallucination: fluent, confident, and wrong. A wrong number that looks right is more dangerous than an error, because nobody catches it._

_Run the same question a few times. You may get a correct version (with the join and filter) on some runs and the wrong version on others. That non-determinism is itself the lesson: you cannot blindly trust a single LLM output. Record what you observe._

**Phase C — Guardrails**

**Why this phase exists**

In the machine translation session, you learned that high-stakes translation — legal, medical — keeps a human in the loop precisely because neural systems hallucinate. NL-to-SQL is high-stakes: business decisions ride on the numbers. Phase C adds the safety layer that turns an impressive demo into something a company can actually trust. Recall your answer to Comprehension Checkpoint 5 — what 'trust' requires. This is where you build it.

Guardrail 1 — Block dangerous operations. The system should only ever read data, never modify or delete it. A hallucinated DROP TABLE would be catastrophic.

FORBIDDEN = \['DROP','DELETE','UPDATE','INSERT','ALTER','TRUNCATE','REPLACE'\]

def is_safe(sql):

upper = sql.upper()

return not any(word in upper for word in FORBIDDEN)

print(is_safe('SELECT COUNT(\*) FROM orders')) # expect True

print(is_safe('DROP TABLE orders')) # expect False

Guardrail 2 — Validate that referenced columns and tables actually exist. This catches the LLM inventing a column that is not in the schema — a common hallucination.

VALID_TABLES = {'customers','products','orders','order_items','returns'}

def references_only_real_tables(sql):

import re

referenced = re.findall(r'FROM\\s+(\\w+)|JOIN\\s+(\\w+)', sql, re.IGNORECASE)

tables = {t for pair in referenced for t in pair if t}

unknown = tables - VALID_TABLES

return (len(unknown) == 0, unknown)

Guardrail 3 — The most important one, and the one your checkpoint-5 answer pointed to: always show the SQL to the human before trusting the answer. The system does not hide its translation; it exposes it for verification.

def trusted_nl2sql(question):

sql = llm_nl2sql(question)

\# Guardrail 1

if not is_safe(sql):

return {'status':'BLOCKED', 'reason':'Dangerous operation', 'sql':sql}

\# Guardrail 2

ok, unknown = references_only_real_tables(sql)

if not ok:

return {'status':'BLOCKED', 'reason':f'Unknown table(s): {unknown}', 'sql':sql}

\# Guardrail 3: run, but ALWAYS return the SQL for human review

result = run_sql(sql)

return {'status':'OK', 'sql':sql, 'answer':result,

'note':'Review the SQL above before trusting this number.'}

import json

print(json.dumps(trusted_nl2sql('How many orders came from Mumbai?'), indent=2))

**Expected output:**

{

"status": "OK",

"sql": "SELECT COUNT(\*) FROM orders WHERE city = 'Mumbai'",

"answer": \[\[31\]\],

"note": "Review the SQL above before trusting this number."

}

**What just happened — trust by design**

_Your system now refuses to run destructive queries, refuses to reference tables that do not exist, and — crucially — never hands over a number without also showing the SQL that produced it. The human can glance at the query and catch the 'repeat customers' kind of error before acting. You have not made the LLM perfect. You have made its mistakes catchable. That is what trust actually means in practice, and it is the same human-in-the-loop principle that high-stakes machine translation depends on._

**PART 4 — Ship It with a UI**

A function in a notebook is not a product. The CEO will never open Colab. She needs a simple screen: a box to type her question, a button, and an answer — with the SQL shown underneath for her to verify. Build one. You may choose either path below; both are acceptable.

**Path 1 — Streamlit (recommended if you are not a front-end developer)**

Streamlit turns a Python script into a web app with no HTML or JavaScript. Save this as app.py and run it. Note: move your database setup, schema, llm_nl2sql, and trusted_nl2sql functions into this file or import them.

\# app.py -- run with: streamlit run app.py

import streamlit as st

st.title('TalkToData — Ask Your Database')

st.write('Type a business question in plain English.')

question = st.text_input('Your question:',

'How many orders came from Mumbai?')

if st.button('Ask'):

result = trusted_nl2sql(question)

if result\['status'\] == 'BLOCKED':

st.error(f"Blocked: {result\['reason'\]}")

st.code(result\['sql'\], language='sql')

else:

st.success('Answer')

st.write(result\['answer'\])

st.caption('Generated SQL (review before trusting):')

st.code(result\['sql'\], language='sql')

st.info(result\['note'\])

_The verification view — showing the SQL beneath every answer — is not decoration. It is Guardrail 3 made visible to the user. This single design choice is what makes the tool trustworthy._

**Path 2 — React / HTML (if you prefer front-end)**

If you would rather build a custom front-end, the contract is simple. Your Python becomes a small backend (Flask or FastAPI) exposing one endpoint that accepts a question and returns the trusted_nl2sql dictionary as JSON. Your React or plain HTML+JavaScript page calls that endpoint and renders three things: the answer, the generated SQL, and the review note. The intelligence stays in Python; the front-end only displays. You are free to design the interface however you like, as long as the SQL is always shown alongside the answer.

\# Minimal Flask backend (backend.py)

from flask import Flask, request, jsonify

app = Flask(\__name_\_)

@app.route('/ask', methods=\['POST'\])

def ask():

question = request.json\['question'\]

return jsonify(trusted_nl2sql(question))

\# Your React/HTML page POSTs {question: '...'} to /ask

\# and renders answer + sql + note from the JSON response.

**PART 5 — Reflect and Deliver**

**The Machine Translation Mapping**

You built an NL-to-SQL engine. But really, you re-lived the entire history of machine translation in miniature. Fill in this reflection table — it ties everything you built back to the session's concepts.

| **Machine translation concept** | **Where it appeared in TalkToData** |
| --- | --- |
| Rule-based translation (RBMT) | Phase A — hand-written keyword rules; brittle, gave up on unseen questions |
| The vocabulary mismatch problem | 'customer' vs the customers table; 'how much sold' vs total_amount |
| Neural/learned translation (NMT) | Phase B — the LLM learned NL->SQL from data; handled joins you never coded |
| The schema as target grammar | The schema in the prompt told the model the rules of the target language |
| Hallucination | Valid SQL that answered the wrong question ('repeat customers' ignored) |
| Faithfulness vs fluency | A query can be fluent (valid SQL) yet unfaithful (wrong question) |
| Human-in-the-loop for high stakes | Phase C — always show the SQL; block dangerous operations |

**The one insight to carry away**

_NL-to-SQL is machine translation where you can check the answer. Every lesson from human-language translation applies — the move from rules to learning, the power and danger of neural models, the necessity of guardrails — but here the wrongness is visible and catchable. That is why it is the perfect place to learn how modern AI translates, and why it must never be trusted blindly._

**What You Will Submit**

<div class="joplin-table-wrapper"><table><tbody><tr><td><p><strong>Deliverable 1 — Your Plan (from Part 2)</strong></p><p>Submitted before your code:</p><ul><li>The five-question mapping table</li><li>Your three phase predictions</li><li>Your one-sentence call on which phase is production-trustworthy</li></ul></td></tr></tbody></table></div>

<div class="joplin-table-wrapper"><table><tbody><tr><td><p><strong>Deliverable 2 — The Working Notebook</strong></p><p>Your Colab notebook with:</p><ul><li>All three phases run, with PREDICT comments and visible outputs</li><li>The hallucination demo, with your recorded observations across multiple runs</li><li>The guardrails working — show a blocked dangerous query</li></ul></td></tr></tbody></table></div>

**Deliverable 3 — The UI**

A working Streamlit app or React/HTML front-end where a non-technical user can type a question and see the answer plus the generated SQL. A screenshot or short screen recording is fine.

<div class="joplin-table-wrapper"><table><tbody><tr><td><p><strong>Deliverable 4 — The Trust Memo (Half a Page)</strong></p><p>Addressed to the CEO, answering the question she cares about most:</p><ul><li>Would you let TalkToData answer questions fully unsupervised, or require human review of the SQL? Defend your position.</li><li>Give one concrete example from your own testing where the system produced a wrong-but-valid answer.</li><li>Name two kinds of questions you would never let it answer without a human checking. Why those?</li><li>Revisit your answer to Comprehension Checkpoint 5. Did your understanding of 'trust' change after building this? How?</li></ul></td></tr></tbody></table></div>

**The Bigger Picture**

NL-to-SQL is one of the fastest-growing applications of language AI in enterprise software, and you have now built a working version of it from first principles. The big players — Microsoft Copilot in Power BI, Google's Looker, Amazon QuickSight Q — are industrial versions of exactly what you built: schema-aware translation from English to SQL, wrapped in guardrails, with the query shown for verification.

You also met, for the third time in this course, the pattern that defines applied NLP. In Session 4 it was regex for structure plus NER for meaning. In Session 5 it was rules for sentiment plus embeddings for topic. Today it was guardrails for safety plus an LLM for translation. The components change; the instinct is permanent — combine the learned model that is powerful with the explicit rules that are trustworthy.

_And you learned the lesson that matters more than any technique: a fluent, confident, valid-looking answer is not the same as a correct one. The engineers who understand that — who build the verification view, who keep the human in the loop, who never trust the machine blindly — are the ones companies depend on. That judgment, not the code, is what you were really here to build._

_"NL-to-SQL is translation you can verify. The machine writes the query; the human still decides whether to trust the answer."_

_— End of Case Study E —_