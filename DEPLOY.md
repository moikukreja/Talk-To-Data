# Deploying TalkToData on Render (free)

Everything below uses **Render's free tier**. The only paid part is the Claude
API key itself (a few cents of usage — see the README).

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
1. Open the **`talktodata-api`** service → **Environment**.
2. Add **`ANTHROPIC_API_KEY`** = your `sk-ant-...` key → **Save Changes**
   (this redeploys the backend).
3. Copy the backend URL from the top of the page, e.g.
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
- **Secrets:** `ANTHROPIC_API_KEY` lives only in Render's dashboard — never in
  the repo. `.env` is git-ignored.
- **Prefer Vercel/Netlify for the frontend instead?** You can: point it at the
  `frontend/` folder, build `npm run build`, output `dist`, and set
  `VITE_API_BASE_URL` the same way. Keep the backend on Render.
