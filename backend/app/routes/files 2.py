from __future__ import annotations

"""File browsing endpoints for EDGE workspace resources."""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, PlainTextResponse
from typing import List
from pathlib import Path
import os

from app.config import ENVIRONMENT  # just to ensure config import works

WORKSPACE_ROOT = Path(os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")).resolve()

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/list", response_model=List[str])
async def list_files(subdir: str | None = None):
    """Return relative file paths under the workspace.

    If *subdir* is provided, list inside that directory.
    """
    base = (WORKSPACE_ROOT / subdir).resolve() if subdir else WORKSPACE_ROOT
    if not base.is_relative_to(WORKSPACE_ROOT):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not base.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    files = []
    for p in base.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(WORKSPACE_ROOT)))
    return files


@router.get("/raw")
async def get_file(path: str):
    """Return the raw contents of *path* inside workspace.

    For binary files >1 MB we return as attachment; small text files are
    returned inline.
    """
    abs_path = (WORKSPACE_ROOT / path).resolve()
    if not abs_path.is_relative_to(WORKSPACE_ROOT):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Heuristic: treat as text if under 1 MB and endswith typical text ext
    text_ext = {".md", ".txt", ".mmd", ".py", ".json", ".yaml", ".yml"}
    if abs_path.suffix in text_ext and abs_path.stat().st_size < 1_000_000:
        return PlainTextResponse(abs_path.read_text())

    # Otherwise send as downloadable file
    return FileResponse(str(abs_path), filename=abs_path.name) 