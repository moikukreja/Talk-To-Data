# Deploying TalkToData on Render (free)

Everything below is **free** — Render's free tier for hosting, and Google AI
Studio's free tier for the Gemini API key (no credit card).

The repo ships a Blueprint ([`render.yaml`](render.yaml)) that creates **two**
free services:

| Service | Type | What it is |
| --- | --- | --- |
| `talktodata-api` | Web Service (Python) | FastAPI backend |
| `talktodata-web` | Static Site | React + TypeScript frontend |

---

## Step 1 — Create the services from the Blueprint
1. Go to **https://dashboard.render.com** → **New +** → **Blueprint**.
2. Connect your GitHub and pick **`moikukreja/Talk-To-Data`**.
3. Render reads `render.yaml` and proposes both services → **Apply**.
4. The first build will run. The frontend's API URL isn't set yet — that's
   expected; we fix it in Step 3.

## Step 2 — Set the API key on the backend
1. Get a free key at **https://aistudio.google.com/apikey** (sign in with Google
   → **Create API key** → copy it).
2. Open the **`talktodata-api`** service → **Environment**.
3. Add **`GEMINI_API_KEY`** = your key → **Save Changes** (this redeploys the
   backend).
4. Copy the backend URL from the top of the page, e.g.
   `https://talktodata-api.onrender.com`.

## Step 3 — Point the frontend at the backend
1. Open the **`talktodata-web`** service → **Environment**.
2. Add **`VITE_API_BASE_URL`** = your backend URL from Step 2
   (e.g. `https://talktodata-api.onrender.com`) → **Save Changes**.
3. **Manual Deploy → Clear build cache & deploy** (Vite bakes the URL in at
   build time, so it must rebuild).
4. Copy the frontend URL, e.g. `https://talktodata-web.onrender.com`.

## Step 4 — Allow the frontend through CORS
1. Back on **`talktodata-api`** → **Environment**.
2. Add **`FRONTEND_ORIGIN`** = your frontend URL from Step 3 → **Save Changes**.
3. Done. Open the frontend URL and ask a question.

---

## Notes
- **Cold starts:** the free backend sleeps after ~15 min idle; the first request
  after it wakes takes ~50s. Subsequent requests are fast. (Ask once to "wake"
  it before a demo.)
- **Secrets:** `GEMINI_API_KEY` lives only in Render's dashboard — never in
  the repo. `.env` is git-ignored.
- **Free-tier limits:** Gemini's free tier allows roughly 15 requests/min and
  ~1,500/day on `gemini-2.0-flash` — far more than this app needs.
- **Prefer Vercel/Netlify for the frontend instead?** You can: point it at the
  `frontend/` folder, build `npm run build`, output `dist`, and set
  `VITE_API_BASE_URL` the same way. Keep the backend on Render.
