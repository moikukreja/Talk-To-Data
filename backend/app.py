"""
TalkToData FastAPI backend.

POST /ask  { "question": "..." }  ->  the trusted_nl2sql() dict:
    success : { status:"OK",      sql, answer, note }
    blocked : { status:"BLOCKED", reason, sql }

The intelligence lives in engine.py; this layer only exposes it over HTTP and
configures CORS for local dev + the production frontend.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from engine import trusted_nl2sql

load_dotenv()  # read backend/.env (GEMINI_API_KEY, FRONTEND_ORIGIN)

app = FastAPI(title="TalkToData", version="1.0.0")

# CORS — local dev (Vite 5173, CRA 3000) + the production deploy URL from .env.
_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
_prod = os.environ.get("FRONTEND_ORIGIN")  # e.g. https://talktodata.vercel.app
if _prod:
    _origins.extend(o.strip() for o in _prod.split(",") if o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    """Translate the question and return the guardrailed result dict."""
    question = (req.question or "").strip()
    if not question:
        return {"status": "BLOCKED", "reason": "Empty question", "sql": ""}
    return trusted_nl2sql(question)
