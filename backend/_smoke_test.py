# Backend smoke test: exercise POST /ask over real HTTP via TestClient,
# stubbing the LLM so no API key is needed. Verifies the consistent dict
# contract for OK / blocked-dangerous / blocked-unknown-table.
import json
import engine
from fastapi.testclient import TestClient

# Stub Claude with a deterministic router so we can test all guardrail paths.
def fake_llm(question, schema=engine.SCHEMA):
    q = question.lower()
    if "mumbai" in q:
        return "SELECT COUNT(*) FROM orders WHERE LOWER(city)='mumbai'"
    if "drop" in q or "delete everything" in q:
        return "DROP TABLE orders"          # simulated hallucinated destructive query
    if "secret" in q:
        return "SELECT * FROM secret_admin_table"  # invented table
    return "SELECT COUNT(*) FROM orders"

engine.llm_nl2sql = fake_llm  # monkeypatch before importing app's reference? app calls engine.trusted_nl2sql which calls module-level llm_nl2sql

# trusted_nl2sql references llm_nl2sql by module global, so patching engine.llm_nl2sql works.
from app import app
client = TestClient(app)

print("health:", client.get("/health").json())

for q in ["How many orders came from Mumbai?",
          "please drop the database",
          "show me the secret admin table",
          "   "]:
    r = client.post("/ask", json={"question": q})
    print(f"\nQ: {q!r}  [HTTP {r.status_code}]")
    print(json.dumps(r.json(), indent=2))

# Assert the consistent contract
ok = client.post("/ask", json={"question": "mumbai orders"}).json()
assert ok["status"] == "OK" and "sql" in ok and "answer" in ok and "note" in ok, ok
blk = client.post("/ask", json={"question": "drop it"}).json()
assert blk["status"] == "BLOCKED" and "reason" in blk and "sql" in blk, blk
print("\nALL CONTRACT ASSERTIONS PASSED")
