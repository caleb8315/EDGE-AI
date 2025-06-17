from __future__ import annotations

"""Tool: file_manager

Simple file read/write operations within a restricted **workspace**
directory to prevent escaping to the host filesystem.
"""

from pathlib import Path
from typing import Literal, Optional

from .base import BaseTool
from app.utils.filesystem import get_user_workspace, is_safe_path


class FileManagerTool(BaseTool):
    name: str = "file_manager"
    description: str = (
        "Read or write small text files in the workspace. Parameters:\n"
        "- mode (str): 'read' or 'write'.\n"
        "- path (str): Relative path inside the user's workspace.\n"
        "- content (str, required for write): Text content.\n"
        "Returns: File content (read) or confirmation (write)."
    )

    async def run(
        self,
        mode: Literal["read", "write"],
        path: str,
        *,
        content: Optional[str] = None,
        auth_user_id: Optional[str] = None,
    ) -> str:  # type: ignore[override]
        if not auth_user_id:
            raise ValueError("auth_user_id must be provided to use the file manager.")

        user_workspace = get_user_workspace(auth_user_id)

        abs_path = (user_workspace / path).resolve()

        # Security check
        if not is_safe_path(abs_path):
            raise ValueError("Access outside user's workspace is not allowed.")

        if mode == "read":
            if not abs_path.exists():
                raise FileNotFoundError(f"File not found in your workspace: {path}")
            return abs_path.read_text()
        elif mode == "write":
            if content is None:
                raise ValueError("'content' must be provided when mode='write'")
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(content)
            return f"File written to {path}"
        else:
            raise ValueError("mode must be 'read' or 'write'") 