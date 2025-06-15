from __future__ import annotations

"""Tool: scrape_website

Fetch the HTML at a given `url` and extract readable text using BeautifulSoup.  Optionally an
*element selector* (CSS selector) can be provided to narrow down the
content.  The output is a plain-text string truncated to a safe length so
that it can be passed to LLM contexts.
"""

import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .base import BaseTool

# Rough upper-bound on characters returned to avoid huge LLM prompts
_MAX_CHARS = 8_000


class ScrapeWebsiteTool(BaseTool):
    name: str = "scrape_website"
    description: str = (
        "Scrape the visible text from a public website. Parameters:\n"
        "- url (str): Complete URL to fetch.\n"
        "- selector (str, optional): CSS selector to target a specific part of the page.\n"
        "Returns: Cleaned plain-text extracted from the page."
    )

    async def run(self, url: str, selector: Optional[str] = None) -> str:  # type: ignore[override]
        """Return cleaned text from *url*.

        Args:
            url: Fully-qualified URL (including http/https).
            selector: Optional CSS selector to scope extraction.
        """
        if not url.lower().startswith(("http://", "https://")):
            raise ValueError("`url` must start with http:// or https://")

        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        if selector:
            elements = soup.select(selector)
            if not elements:
                raise ValueError(f"CSS selector '{selector}' matched no elements on the page")
            text = "\n".join(_element_text(el) for el in elements)
        else:
            text = soup.get_text(separator="\n")

        # Collapse whitespace and truncate
        text = _clean_whitespace(text)
        return text[:_MAX_CHARS]


def _clean_whitespace(text: str) -> str:
    """Collapse consecutive whitespace/newlines for cleaner output."""
    # Replace multiple whitespace with single space, but keep newlines
    text = re.sub(r"[ \t\x0b\f\r]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)  # limit consecutive newlines
    return text.strip()


def _element_text(element) -> str:
    """Return cleaned text for a BeautifulSoup element."""
    return _clean_whitespace(element.get_text(separator="\n")) 