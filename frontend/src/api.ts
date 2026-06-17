import type { AskResponse } from "./types";

// API base URL from an environment variable — never a hardcoded localhost in
// production. Falls back to localhost for dev.
const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error(`Server responded with ${res.status} ${res.statusText}`);
  }

  return (await res.json()) as AskResponse;
}
