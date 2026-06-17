import { JSX } from "react";
import type { SqlAnswer } from "../types";

// Renders the OK-path answer: a "SQL ERROR: ..." string, an empty result, or a
// small table of rows. Defensive against any shape so it never crashes.

interface AnswerViewProps {
  answer: SqlAnswer;
}

export function AnswerView({ answer }: AnswerViewProps): JSX.Element {
  if (typeof answer === "string") {
    return <div className="answer answer--error">{answer}</div>;
  }

  if (!Array.isArray(answer) || answer.length === 0) {
    return <div className="answer answer--empty">No rows returned.</div>;
  }

  // Single scalar result (e.g. a COUNT / AVG) — show it big.
  if (answer.length === 1 && answer[0].length === 1) {
    const cell = answer[0][0];
    return <div className="answer answer--scalar">{formatCell(cell)}</div>;
  }

  return (
    <div className="answer answer--table">
      <table>
        <tbody>
          {answer.map((row, r) => (
            <tr key={r}>
              {row.map((cell, c) => (
                <td key={c}>{formatCell(cell)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatCell(cell: string | number | null): string {
  if (cell === null) return "NULL";
  if (typeof cell === "number") {
    return Number.isInteger(cell) ? String(cell) : cell.toFixed(2);
  }
  return cell;
}
