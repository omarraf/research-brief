import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import serpapi
import anthropic

SERPAPI_API_KEY = os.environ["SERPAPI_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

app = FastAPI(title="Research Brief Bot")
app.mount("/static", StaticFiles(directory="static"), name="static")

serp_client = serpapi.Client(api_key=SERPAPI_API_KEY)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_executor = ThreadPoolExecutor(max_workers=3)


def _fetch_scholar(query: str) -> list[dict]:
    try:
        results = serp_client.search({
            "engine": "google_scholar",
            "q": query,
            "num": 5,
        })
        return results.get("organic_results", [])[:5]
    except Exception:
        return []


def _fetch_news(query: str) -> list[dict]:
    try:
        results = serp_client.search({
            "engine": "google_news",
            "q": query,
        })
        return results.get("news_results", [])[:5]
    except Exception:
        return []


def _fetch_web(query: str) -> list[dict]:
    try:
        results = serp_client.search({
            "engine": "google",
            "q": query,
            "num": 5,
        })
        return results.get("organic_results", [])[:5]
    except Exception:
        return []


async def _fetch_all(query: str) -> tuple[list, list, list]:
    loop = asyncio.get_event_loop()
    scholar, news, web = await asyncio.gather(
        loop.run_in_executor(_executor, _fetch_scholar, query),
        loop.run_in_executor(_executor, _fetch_news, query),
        loop.run_in_executor(_executor, _fetch_web, query),
    )
    return scholar, news, web


def _build_context(scholar: list, news: list, web: list) -> str:
    lines: list[str] = []

    if scholar:
        lines.append("### Academic Sources (Google Scholar)")
        for r in scholar:
            title = r.get("title", "Untitled")
            link = r.get("link", "")
            snippet = r.get("snippet", "No abstract available.")
            pub = r.get("publication_info", {}).get("summary", "")
            linked_title = f"[{title}]({link})" if link else f"**{title}**"
            lines.append(f"- {linked_title}{f' ({pub})' if pub else ''}: {snippet}")

    if news:
        lines.append("\n### Recent News")
        for r in news:
            title = r.get("title", "Untitled")
            link = r.get("link", "")
            snippet = r.get("snippet", "")
            source = r.get("source", {})
            source_name = source.get("name", "") if isinstance(source, dict) else str(source)
            linked_title = f"[{title}]({link})" if link else f"**{title}**"
            lines.append(f"- {linked_title}{f' ({source_name})' if source_name else ''}: {snippet}")

    if web:
        lines.append("\n### Web Sources")
        for r in web:
            title = r.get("title", "Untitled")
            link = r.get("link", "")
            snippet = r.get("snippet", "")
            linked_title = f"[{title}]({link})" if link else f"**{title}**"
            lines.append(f"- {linked_title}: {snippet}")

    return "\n".join(lines) if lines else "No search results retrieved."


SYSTEM_PROMPT = """\
You are a professional research analyst. When given search results, you write comprehensive, \
well-structured research briefs in Markdown. Be thorough but concise. Use headers, bullet \
points, and bold text to aid readability. Always hyperlink sources using the markdown links \
provided in the search results — never drop a URL or rewrite it as plain text.\
"""

BRIEF_TEMPLATE = """\
Write a research brief on: **{query}**

Use this structure:
1. **Executive Summary** — 2–3 sentence overview of the topic
2. **Key Findings** — 4–6 bullet points synthesising the most important insights
3. **Academic Perspective** — what the scholarly sources reveal
4. **Recent Developments** — notable news and emerging trends
5. **Implications & Outlook** — what this means, and what to watch

--- SEARCH RESULTS ---
{context}
--- END SEARCH RESULTS ---
"""


@app.get("/")
async def index():
    with open("static/index.html") as f:
        return HTMLResponse(f.read())


@app.get("/api/brief")
async def generate_brief(q: str = Query(..., min_length=1, max_length=500)):
    scholar, news, web = await _fetch_all(q)

    if not scholar and not news and not web:
        raise HTTPException(status_code=502, detail="All search sources failed. Check your SERPAPI_API_KEY.")

    context = _build_context(scholar, news, web)
    prompt = BRIEF_TEMPLATE.format(query=q, context=context)

    def stream():
        with claude.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as s:
            for chunk in s.text_stream:
                yield chunk

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")
