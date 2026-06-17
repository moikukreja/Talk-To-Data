import { JSX } from "react";

// Guardrail 3, made visible. The SQL viewer is the core trust mechanism — it is
// always rendered alongside every answer so a human can verify the translation.
// A tiny self-contained highlighter (no external dependency) keeps the build
// robust; it must handle null / empty SQL without crashing.

const KEYWORDS = new Set([
  "SELECT", "FROM", "WHERE", "JOIN", "INNER", "LEFT", "RIGHT", "OUTER", "ON",
  "GROUP", "BY", "ORDER", "LIMIT", "HAVING", "AS", "AND", "OR", "NOT", "IN",
  "COUNT", "SUM", "AVG", "MIN", "MAX", "DISTINCT", "DESC", "ASC", "LOWER",
  "UPPER", "LIKE", "UNION", "NULL", "IS",
]);

function highlight(sql: string): JSX.Element[] {
  // Split into tokens while keeping delimiters (whitespace, punctuation, quotes).
  const tokens = sql.match(/'[^']*'|"[^"]*"|\w+|\s+|[^\s\w]/g) ?? [];
  return tokens.map((tok, i) => {
    let cls = "tok";
    if (/^'[^']*'$|^"[^"]*"$/.test(tok)) {
      cls = "tok tok-string";
    } else if (/^\d+(\.\d+)?$/.test(tok)) {
      cls = "tok tok-number";
    } else if (KEYWORDS.has(tok.toUpperCase())) {
      cls = "tok tok-keyword";
    } else if (/^[^\s\w]$/.test(tok)) {
      cls = "tok tok-punct";
    }
    return (
      <span key={i} className={cls}>
        {tok}
      </span>
    );
  });
}

interface SqlViewerProps {
  sql: string | null | undefined;
}

export function SqlViewer({ sql }: SqlViewerProps): JSX.Element {
  const safe = (sql ?? "").trim();
  return (
    <div className="sql-viewer">
      <div className="sql-viewer__label">Generated SQL (Guardrail 3 — verify before trusting)</div>
      <pre className="sql-viewer__code" aria-label="Generated SQL">
        {safe.length === 0 ? (
          <span className="tok tok-muted">— no SQL was generated —</span>
        ) : (
          <code>{highlight(safe)}</code>
        )}
      </pre>
    </div>
  );
}
