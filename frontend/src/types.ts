// The exact shapes the FastAPI /ask endpoint returns. A response is always one
// of these two — discriminated by `status`.

/** A SQL result is rows of cells, or a "SQL ERROR: ..." string from the engine. */
export type SqlAnswer = Array<Array<string | number | null>> | string;

export interface OkResponse {
  status: "OK";
  sql: string;
  answer: SqlAnswer;
  note: string;
}

export interface BlockedResponse {
  status: "BLOCKED";
  sql: string;
  reason: string;
}

export type AskResponse = OkResponse | BlockedResponse;
