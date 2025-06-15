from __future__ import annotations

"""Tool: file_manager

Simple file read/write operations within a restricted **workspace**
directory to prevent escaping to the host filesystem.
"""

import os
from pathlib import Path
from typing import Literal, Optional

from .base import BaseTool


_WORKSPACE_ROOT = Path(os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")).resolve()
_WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)


class FileManagerTool(BaseTool):
    name: str = "file_manager"
    description: str = (
        "Read or write small text files in the workspace. Parameters:\n"
        "- mode (str): 'read' or 'write'.\n"
        "- path (str): Relative path inside workspace.\n"
        "- content (str, required for write): Text content.\n"
        "Returns: File content (read) or confirmation (write)."
    )

    async def run(
        self,
        mode: Literal["read", "write"],
        path: str,
        *,
        content: Optional[str] = None,
    ) -> str:  # type: ignore[override]
        abs_path = (_WORKSPACE_ROOT / path).resolve()
        if abs_path.is_relative_to(_WORKSPACE_ROOT):  # py311+
            pass
        else:
            raise ValueError("Access outside workspace is not allowed.")

        if mode == "read":
            if not abs_path.exists():
                raise FileNotFoundError(str(abs_path))
            return abs_path.read_text()
        elif mode == "write":
            if content is None:
                raise ValueError("'content' must be provided when mode='write'")
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(content)
            return f"File written to {abs_path}"
        else:
            raise ValueError("mode must be 'read' or 'write'") 