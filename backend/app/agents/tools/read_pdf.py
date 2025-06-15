from __future__ import annotations

"""Tool: read_pdf

Extract text from a PDF file (local path or URL).
Currently uses the `pdfplumber` library.  If it's not installed the tool
will raise a helpful error.
"""

import os
from pathlib import Path
from typing import Optional

import httpx

from .base import BaseTool

try:
    import pdfplumber  # type: ignore
except ImportError:  # pragma: no cover
    pdfplumber = None  # type: ignore


class ReadPDFTool(BaseTool):
    name: str = "read_pdf"
    description: str = (
        "Extract plaintext from a PDF file. Parameters:\n"
        "- source (str): Local file path or URL.\n"
        "Returns: Extracted text (may be truncated)."
    )

    async def run(self, source: str, *, max_pages: Optional[int] = None) -> str:  # type: ignore[override]
        if pdfplumber is None:
            raise RuntimeError("`pdfplumber` library not installed. Run `pip install pdfplumber`. ")

        # Download if URL
        if source.lower().startswith("http"):
            async with httpx.AsyncClient() as client:
                resp = await client.get(source)
                resp.raise_for_status()
                tmp_path = Path("/tmp/download.pdf")
                tmp_path.write_bytes(resp.content)
                path = tmp_path
        else:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(str(path))

        text_parts = []
        with pdfplumber.open(str(path)) as pdf:
            for i, page in enumerate(pdf.pages):
                if max_pages is not None and i >= max_pages:
                    break
                text_parts.append(page.extract_text() or "")
        return "\n\n".join(text_parts) 