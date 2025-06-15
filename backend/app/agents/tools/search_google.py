from __future__ import annotations

"""Tool: search_google

Lightweight search utility that returns the titles + URLs for the first few
web results.  It uses the *duckduckgo-search* package so it works without
sign-up keys, but the name stays "search_google" for familiarity.
"""

from typing import List

from .base import BaseTool

try:
    from duckduckgo_search import DDGS  # type: ignore
except ImportError:  # pragma: no cover
    DDGS = None  # type: ignore


class SearchGoogleTool(BaseTool):
    name: str = "search_google"
    description: str = (
        "Search the web and return (title, url) pairs for the top N results. Parameters:\n"
        "- query (str): Search term.\n"
        "- max_results (int, optional): Defaults to 5.\n"
        "Returns: List[dict] with `title` and `href`."
    )

    async def run(self, query: str, max_results: int = 5) -> List[dict]:  # type: ignore[override]
        if DDGS is None:
            raise RuntimeError("`duckduckgo-search` not installed. Run `pip install duckduckgo-search`. ")

        # duckduckgo-search has synchronous api – run in thread to keep async.
        import asyncio, functools

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, functools.partial(_search, query, max_results))
        return results


def _search(query: str, max_results: int) -> List[dict]:
    out: List[dict] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):  # type: ignore[attr-defined]
            out.append({"title": r["title"], "href": r["href"]})
    return out 