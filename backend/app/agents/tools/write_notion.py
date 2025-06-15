from __future__ import annotations

"""Tool: write_notion

Send structured content or plain text to a Notion database or page.

This is **currently a stub implementation**.  To enable it you will need to
set the NOTION_API_KEY environment variable and (optionally) the
NOTION_DATABASE_ID.  The tool will then create or update pages.
"""

import os
from typing import Any, Dict, Optional

from .base import BaseTool

try:
    from notion_client import AsyncClient as NotionClient  # type: ignore
except ImportError:  # pragma: no cover
    NotionClient = None  # type: ignore


def _get_client() -> "NotionClient":  # type: ignore
    if NotionClient is None:
        raise RuntimeError("`notion-client` package is not installed. Run `pip install notion-client`. ")

    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        raise RuntimeError("Missing NOTION_API_KEY environment variable.")
    return NotionClient(auth=api_key)


class WriteNotionTool(BaseTool):
    name: str = "write_notion"
    description: str = (
        "Create or update a Notion page. Parameters:\n"
        "- title (str): Page title.\n"
        "- content (str): Markdown/plain-text body.\n"
        "- database_id (str, optional): Target Notion database — if omitted a standalone page is created.\n"
        "Returns: URL to the created/updated Notion page.  (Stub returns placeholder.)"
    )

    async def run(self, title: str, content: str, database_id: Optional[str] = None) -> str:  # type: ignore[override]
        # Placeholder behaviour – just echo parameters until Notion credentials are supplied.
        if not os.getenv("NOTION_API_KEY"):
            return (
                "[write_notion stub] NOTION_API_KEY not set — pretending to create page '"
                f"{title}'. Content length={len(content)} chars."
            )

        client = _get_client()

        # Minimal Notion page creation example (title + markdown in callout).
        # Production code should handle rich-text blocks, databases, etc.
        if database_id:
            page = await client.pages.create(  # type: ignore[attr-defined]
                parent={"database_id": database_id},
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {"content": title},
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": content}}]
                        },
                    }
                ],
            )
        else:
            page = await client.pages.create(  # type: ignore[attr-defined]
                parent={"type": "workspace", "workspace": True},
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {"content": title},
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": content}}]
                        },
                    }
                ],
            )

        url = page.get("url", "https://www.notion.so/")
        return url 