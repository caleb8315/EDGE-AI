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

        # Get workspace root for uploaded files
        workspace_root = Path(os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")).resolve()

        # Download if URL
        if source.lower().startswith("http"):
            async with httpx.AsyncClient() as client:
                resp = await client.get(source)
                resp.raise_for_status()
                tmp_path = Path("/tmp/download.pdf")
                tmp_path.write_bytes(resp.content)
                path = tmp_path
        else:
            # Check if it's a relative path in workspace first
            if not source.startswith('/'):
                workspace_path = workspace_root / source
                if workspace_path.exists():
                    path = workspace_path
                else:
                    path = Path(source)
            else:
                path = Path(source)
            
            if not path.exists():
                # Try to give helpful error if it might be in workspace
                available_pdfs = list(workspace_root.rglob("*.pdf"))
                if available_pdfs:
                    pdf_list = "\n".join([str(p.relative_to(workspace_root)) for p in available_pdfs[:5]])
                    raise FileNotFoundError(f"PDF not found: {source}. Available PDFs in workspace:\n{pdf_list}")
                else:
                    raise FileNotFoundError(f"PDF not found: {source}. No PDFs found in workspace.")

        text_parts = []
        try:
            with pdfplumber.open(str(path)) as pdf:
                total_pages = len(pdf.pages)
                pages_to_read = min(total_pages, max_pages or total_pages)
                
                text_parts.append(f"📄 PDF: {path.name} ({total_pages} pages, reading {pages_to_read})\n")
                
            for i, page in enumerate(pdf.pages):
                if max_pages is not None and i >= max_pages:
                    break
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_parts.append(f"--- Page {i+1} ---\n{page_text}")
                
                if max_pages and total_pages > max_pages:
                    text_parts.append(f"\n... (truncated at {max_pages} pages, {total_pages - max_pages} pages remaining)")
                    
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF {path}: {str(e)}")
            
        return "\n\n".join(text_parts) 