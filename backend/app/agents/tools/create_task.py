from __future__ import annotations

"""Tool: create_task

Create a new EDGE task (and persist it to Supabase/mock DB).  This can be
used by agents to track follow-up work items.
"""

import uuid
import re
from typing import Literal, Optional

from app.services.supabase_service import supabase_service
from .base import BaseTool

_Status = Literal["pending", "in_progress", "completed"]


class CreateTaskTool(BaseTool):
    name: str = "create_task"
    description: str = (
        "Create a task and assign it to an EDGE role. Parameters:\n"
        "- user_id (str): UUID of the human user who owns the task.\n"
        "- assigned_to_role (str): CEO | CTO | CMO\n"
        "- description (str): Task summary.\n"
        "- status (str, optional): pending | in_progress | completed (default pending).\n"
        "- resources (list[str], optional): List of resources associated with the task."
    )

    async def run(
        self,
        assigned_to_role: str,
        description: str,
        user_id: Optional[str] = None,
        status: _Status = "pending",
        resources: Optional[list[str]] = None,
    ) -> str:  # type: ignore[override]
        # Ensure user_id is a valid UUID
        _uid = user_id
        if not _uid or not re.fullmatch(r"[0-9a-fA-F-]{36}", _uid):
            _uid = str(uuid.uuid4())

        data = {
            "id": str(uuid.uuid4()),
            "user_id": _uid,
            "assigned_to_role": assigned_to_role.upper(),
            "description": description,
            "status": status,
            "resources": resources or [],
        }
        await supabase_service.create_task(data)
        return f"Task '{description[:40]}...' created and assigned to {assigned_to_role.upper()}" 