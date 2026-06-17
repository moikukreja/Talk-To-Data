# TalkToData — Ask Your Database in Plain English

Case Study E · NL-to-SQL · MAIB, SP Jain Dubai.

An NL-to-SQL engine built in three phases (rule-based → LLM → guardrails),
exposed through a **FastAPI** backend and a **React + TypeScript** frontend.
LLM provider: **Anthropic Claude `claude-sonnet-4-6`**.

## Deliverables
1. **Solution plan** — in the notebook (Deliverable 1 section) and the chat transcript.
2. **Colab notebook** — [`notebook/TalkToData_NL2SQL.ipynb`](notebook/TalkToData_NL2SQL.ipynb): all three phases, PREDICT comments, the hallucination demo run 3×, a blocked dangerous query, and the Part 5 reflection table. `random.seed(42)`, fully Colab-compatible (`!pip` installs, in-memory DB, no local paths).
3. **App** — `backend/` (FastAPI) + `frontend/` (React + TypeScript, Vite).
4. **Trust memo** — [`TRUST_MEMO.md`](TRUST_MEMO.md).

---

## Running the app locally

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then put your real ANTHROPIC_API_KEY in .env
uvicorn app:app --reload --port 8000
```
- `POST /ask  { "question": "..." }` → `{status, sql, answer, note}` or `{status, reason, sql}`.
- `GET /health` → `{ "status": "ok" }`.

### 2. Frontend (React + TypeScript)
```bash
cd frontend
npm install
cp .env.example .env.local   # VITE_API_BASE_URL=http://localhost:8000
npm run dev                  # http://localhost:5173
```

For every response the UI always renders three things: the **answer or blocked
reason**, the **generated SQL** (syntax-highlighted — Guardrail 3 made visible),
and the **review note**. Loading and error states are both handled; the layout
is mobile-responsive.

---

## Deploying

**Frontend (Vercel / Netlify):** build command `npm run build`, output `dist/`.
Set `VITE_API_BASE_URL` to your deployed backend URL in the dashboard.

**Backend:** deploy `backend/` (e.g. Render / Railway / Fly). Set `ANTHROPIC_API_KEY`
and `FRONTEND_ORIGIN` (your deployed frontend URL, comma-separated for multiple)
so CORS allows the production site.

---

## Security & reproducibility notes
- **No hardcoded keys.** The key is read from the environment / `.env` only.
- **Guardrails.** Destructive SQL (`DROP/DELETE/UPDATE/INSERT/ALTER/TRUNCATE/REPLACE`)
  is blocked on whole-word match; queries referencing non-existent tables are blocked;
  the SQL is always returned for human review.
- **Thread-safety.** The in-memory SQLite DB uses `check_same_thread=False` + a lock,
  seeded once at startup with `random.seed(42)` — identical data to the notebook.
