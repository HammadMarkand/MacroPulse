# MacroPulse — GitHub-Ready (Frontend + Backend)

This repo contains:
- **frontend/** (React + Vite) — deploys to **Netlify** (SPA routing configured)
- **backend/** (FastAPI) — run locally with Python or Docker; deploy to AWS later

## 0) Clone and push to your GitHub
```bash
# from the folder containing this README
git init
git branch -M main
git add .
git commit -m "MacroPulse initial commit"
git remote add origin https://github.com/YOUR_USERNAME/macropulse.git
git push -u origin main
```

## 1) Connect to Netlify (Frontend)
1. Go to **Netlify → Add new site → Import from Git**.
2. Select your `macropulse` GitHub repo.
3. Netlify reads **netlify.toml** automatically:
   - Base directory: `frontend`
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`
   - SPA redirects: `/* -> /index.html` (status 200)
4. In Netlify **Site settings → Environment variables**, add:
   - `VITE_API_BASE` = `https://YOUR_BACKEND_DOMAIN` (or `http://127.0.0.1:8000` for local dev via a tunnel)

Deploy and open your site. Routes `/charts` & `/health` will work.

## 2) Run the backend locally (FastAPI)
### Option A: Python (recommended for quick test)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

export DATABASE_URL=sqlite:///./macropulse.db
export FRED_API_KEY=YOUR_FRED_KEY
export CRON_TOKEN="your-strong-secret"

python3 -m uvicorn backend.main:app --reload
# API on http://127.0.0.1:8000
```

Then trigger initial data:
```bash
curl -s -X POST 'http://127.0.0.1:8000/data/refresh/fred/secure'   -H "X-CRON-TOKEN: your-strong-secret" | python3 -m json.tool
```

### Option B: Docker
```bash
docker build -t macropulse-backend -f backend/Dockerfile .
docker run --rm -p 8000:8000   -e DATABASE_URL=sqlite:///./macropulse.db   -e FRED_API_KEY=YOUR_FRED_KEY   -e CRON_TOKEN=your-strong-secret   macropulse-backend
```

## 3) Point frontend to backend
- On **Netlify**, set `VITE_API_BASE` to your backend API base URL.
- If backend is local and Netlify is remote, use a tunnel (e.g., `cloudflared tunnel` or `ngrok`) and put that URL in `VITE_API_BASE`.

## 4) AWS Deploy (later)
Use the CloudFormation templates we prepared earlier (schedulers, ECS/ALB). Ping me when ready and I’ll wire the one-click ECS stack for you.

---

### Default Frontend Pages
- `/charts` — FEDFUNDS, UNRATE, CPIAUCSL, GDPC1
- `/health` — data staleness dashboard

### API Highlights
- `POST /data/refresh/fred/secure` (header `X-CRON-TOKEN` required)
- `GET /data/series/{code}`
- `GET /data/health/data`
