from __future__ import annotations

"""Tool: create_task

Create a new EDGE task (and persist it to Supabase/mock DB).  This can be
used by agents to track follow-up work items.
"""

from pathlib import Path
from typing import List, Literal, Optional

from app.models import RoleEnum, TaskStatusEnum
from app.services.supabase_service import supabase_service
from app.utils.filesystem import get_user_workspace, is_safe_path
from .base import BaseTool

_Status = Literal["pending", "in_progress", "completed"]


class CreateTaskTool(BaseTool):
    name: str = "create_task"
    description: str = (
        "Create a new task, and optionally create a file as a resource for it. Parameters:\n"
        "- description (str): The task description.\n"
        "- assigned_to_role (str): Role to assign the task to (CEO, CTO, CMO).\n"
        "- user_id (str): The user's ID to associate the task with.\n"
        "- status (str, optional): 'pending', 'in_progress', or 'completed'.\n"
        "- resource_path (str, optional): If creating a file, the path to save it to.\n"
        "- resource_content (str, optional): The content to write to the new file.\n"
        " If resource_path is omitted but resource_content is supplied, the tool will automatically create a suitable path with the correct file extension based on the content (defaulting to Python `.py`)."
    )

    async def run(
        self,
        description: str,
        assigned_to_role: RoleEnum,
        user_id: str,
        status: TaskStatusEnum = "pending",
        resource_path: Optional[str] = None,
        resource_content: Optional[str] = None,
    ) -> str:  # type: ignore[override]
        """Run the tool to create a task in Supabase, with an optional file."""
        
        resources = []
        
        # If resource content and path are provided, create the file
        if resource_path and resource_content is not None:
            try:
                user_workspace = get_user_workspace(user_id)

                abs_path = (user_workspace / resource_path).resolve()
                if not is_safe_path(abs_path):
                    raise ValueError("Access outside user's workspace is not allowed.")

                abs_path.parent.mkdir(parents=True, exist_ok=True)
                abs_path.write_text(resource_content)
                resources.append(resource_path)
            except Exception as e:
                return f"Failed to create resource file: {e}"
        else:
            # Auto-generate a resource path if content is provided without a path
            if resource_content is not None and resource_path is None:
                import uuid, re

                # --- Heuristic language detection ---------------------------------
                _lower = resource_content.lower()
                if "<html" in _lower or "<!doctype html" in _lower:
                    ext = ".html"
                elif "import react" in _lower or "react." in _lower:
                    ext = ".jsx"
                elif re.search(r"\binterface\s+\w+\s*{", resource_content):
                    ext = ".ts"
                elif "def " in _lower or "import " in _lower:
                    ext = ".py"
                else:
                    ext = ".txt"

                filename = f"ai_output_{uuid.uuid4().hex[:8]}{ext}"
                resource_path = f"generated/{filename}"

                try:
                    user_workspace = get_user_workspace(user_id)

                    abs_path = (user_workspace / resource_path).resolve()
                    if not is_safe_path(abs_path):
                        raise ValueError("Access outside user's workspace is not allowed.")

                    abs_path.parent.mkdir(parents=True, exist_ok=True)
                    abs_path.write_text(resource_content)
                    resources.append(resource_path)
                except Exception as e:
                    return f"Failed to create auto-generated resource file: {e}"

        # Find the user's database ID from their auth_id
        db_user = await supabase_service.get_user_by_auth_id(user_id)
        if not db_user:
            # Fallback for old system that used db id
            db_user = await supabase_service.get_user_by_id(user_id)
            if not db_user:
                raise ValueError(f"No user found with id or auth_id: {user_id}")

        task_data = {
            "user_id": db_user["id"],
            "auth_user_id": db_user["auth_user_id"],
            "description": description,
            "assigned_to_role": assigned_to_role,
            "status": status,
            "resources": resources,
        }
        try:
            await supabase_service.create_task(task_data)
            if resources:
                return f"Task created and file '{resource_path}' saved."
            return f"Task created: {description}"
        except Exception as e:
            return f"Failed to create task: {e}" 