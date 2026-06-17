import { FormEvent, JSX, useState } from "react";
import { askQuestion } from "./api";
import type { AskResponse } from "./types";
import { SqlViewer } from "./components/SqlViewer";
import { AnswerView } from "./components/AnswerView";
import "./styles.css";

const SAMPLES = [
  "How many orders came from Mumbai?",
  "Which product category earns the most revenue?",
  "What is the average order value for repeat customers?",
  "List the top 5 cities by number of customers.",
];

export function App(): JSX.Element {
  const [question, setQuestion] = useState<string>(SAMPLES[0]);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk(e: FormEvent): Promise<void> {
    e.preventDefault();
    if (!question.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await askQuestion(question.trim());
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>TalkToData</h1>
        <p>Ask your database a question in plain English.</p>
      </header>

      <form className="ask" onSubmit={handleAsk}>
        <input
          className="ask__input"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. How many orders came from Mumbai?"
          aria-label="Your question"
        />
        <button className="ask__button" type="submit" disabled={loading || !question.trim()}>
          {loading ? "Asking…" : "Ask"}
        </button>
      </form>

      <div className="samples">
        {SAMPLES.map((s) => (
          <button
            key={s}
            type="button"
            className="samples__chip"
            onClick={() => setQuestion(s)}
            disabled={loading}
          >
            {s}
          </button>
        ))}
      </div>

      {loading && (
        <div className="state state--loading" role="status">
          Translating your question and checking the guardrails…
        </div>
      )}

      {error && (
        <div className="state state--error" role="alert">
          <strong>Could not reach the server.</strong> {error}
        </div>
      )}

      {result && <ResultCard result={result} />}
    </div>
  );
}

function ResultCard({ result }: { result: AskResponse }): JSX.Element {
  const blocked = result.status === "BLOCKED";
  return (
    <section className={`result ${blocked ? "result--blocked" : "result--ok"}`}>
      {/* 1) The answer, or the blocked reason — always rendered. */}
      {blocked ? (
        <div className="result__blocked">
          <span className="badge badge--blocked">BLOCKED</span>
          <p className="result__reason">{result.reason}</p>
        </div>
      ) : (
        <div className="result__answer">
          <span className="badge badge--ok">OK</span>
          <AnswerView answer={result.answer} />
        </div>
      )}

      {/* 2) The generated SQL — always rendered (Guardrail 3). */}
      <SqlViewer sql={result.sql} />

      {/* 3) The review note — always visible, never hidden. */}
      <div className="result__note">
        {blocked
          ? "This query was blocked before running. The SQL above is shown so you can see exactly what the model produced."
          : result.note}
      </div>
    </section>
  );
}
