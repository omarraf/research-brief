# Research Brief Bot

A FastAPI app that concurrently fetches Google Scholar, Google News, and Google Web results via SerpAPI, then streams a structured research brief from Claude back to the browser in real time.

## Local development

### Prerequisites

- Python 3.11+
- A [SerpAPI](https://serpapi.com/) API key
- An [Anthropic](https://console.anthropic.com/) API key

### Setup

```bash
# 1. Clone / enter the project directory
cd research-brief

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Export environment variables
export SERPAPI_API_KEY=your_serpapi_key_here
export ANTHROPIC_API_KEY=your_anthropic_key_here

# 5. Run the server
uvicorn main:app --reload
```

Open http://localhost:8000 in your browser.

## Deploying to Railway

### One-click via CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Log in
railway login

# Create a new project from this directory
railway init

# Set environment variables
railway variables set SERPAPI_API_KEY=your_serpapi_key_here
railway variables set ANTHROPIC_API_KEY=your_anthropic_key_here

# Deploy
railway up
```

Railway will detect `railway.toml` and use Nixpacks to build and run `uvicorn main:app --host 0.0.0.0 --port $PORT`.

### Via Railway dashboard

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
2. Connect this repo.
3. In **Variables**, add `SERPAPI_API_KEY` and `ANTHROPIC_API_KEY`.
4. Railway auto-detects `railway.toml` and deploys on every push to main.

## Architecture

```
Browser  ──GET /api/brief?q=...──►  FastAPI
                                       │
                          asyncio.gather() with ThreadPoolExecutor
                          ┌────────────┬─────────────┬────────────┐
                     Scholar (SerpAPI) News (SerpAPI) Web (SerpAPI)
                          └────────────┴─────────────┴────────────┘
                                       │
                          Build prompt from results
                                       │
                          Anthropic claude-sonnet-4-20250514
                                       │
                    StreamingResponse (text/plain) ──► Browser
                    (marked.js renders markdown live)
```

## Environment variables

| Variable           | Description                         |
|--------------------|-------------------------------------|
| `SERPAPI_API_KEY`  | SerpAPI key for search results      |
| `ANTHROPIC_API_KEY`| Anthropic key for Claude streaming  |
