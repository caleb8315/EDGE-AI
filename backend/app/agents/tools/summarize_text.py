from __future__ import annotations

"""Tool: summarize_text

Quickly produce a concise summary of a longer text using the existing
`OpenAIService` abstraction.
"""

from typing import Optional

from app.services.openai_service import openai_service
from .base import BaseTool


class SummarizeTextTool(BaseTool):
    name: str = "summarize_text"
    description: str = (
        "Summarize a block of text. Parameters:\n"
        "- text (str): Content to summarize.\n"
        "- max_words (int, optional): Target summary length.\n"
        "Returns: Summary string."
    )

    async def run(self, text: str, max_words: int = 150) -> str:  # type: ignore[override]
        prompt = (
            "You are a helpful assistant that summarizes text. "
            f"Please summarize the following content in <= {max_words} words:\n\n{text}"
        )
        # openai_service currently works with roles – bypass using direct completions helper
        try:
            client = openai_service.client  # type: ignore[attr-defined]
        except AttributeError:
            client = None
        if client is None:
            return text[:max_words] + ("..." if len(text.split()) > max_words else "")

        resp = await client.chat.completions.create(  # type: ignore[func-returns-value]
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=256,
        )
        return resp.choices[0].message.content.strip() 