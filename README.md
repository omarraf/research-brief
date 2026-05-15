# Research Brief Bot

A FastAPI app that concurrently fetches Google Scholar, Google News, and Google Web results via SerpAPI, then streams a structured research brief from Claude back to the browser in real time.

**Live demo:** https://research-brief-production-bda3.up.railway.app/

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


## Architecture
<img width="500" height="600" alt="image" src="https://github.com/user-attachments/assets/e857bcec-5bd3-446f-a5eb-4f0fd9f9c585" />



## Environment variables

| Variable           | Description                         |
|--------------------|-------------------------------------|
| `SERPAPI_API_KEY`  | SerpAPI key for search results      |
| `ANTHROPIC_API_KEY`| Anthropic key for Claude streaming  |
