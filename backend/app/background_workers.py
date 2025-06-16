import asyncio
import logging
import os
from pathlib import Path
from typing import List, Dict, Any
import re

from app.services.supabase_service import supabase_service
from app.services.openai_service import openai_service

# Workspace root is shared with the file_manager tool & /api/files endpoints
WORKSPACE_ROOT = Path(os.getenv("EDGE_WORKSPACE", "/tmp/edge_workspace")).resolve()

logger = logging.getLogger(__name__)

_POLL_INTERVAL_SEC = 30  # how often to look for new pending tasks


async def _fetch_pending_tasks() -> List[Dict[str, Any]]:
    """Return a list of tasks (dicts) that are still pending."""
    # When running without a real Supabase instance we use the in-memory mock
    if not supabase_service.client:
        return [t for t in supabase_service._mock_tasks.values() if t.get("status") == "pending"]

    # Supabase mode – query directly on the table
    try:
        response = supabase_service.client.table("tasks").select("*").eq("status", "pending").execute()
        return response.data or []
    except Exception as exc:
        logger.error(f"Failed to query pending tasks: {exc}")
        return []


async def _infer_filename_and_content(task: Dict[str, Any]) -> tuple[str, str]:
    """Return (relative_path, file_content) that fulfils *task*."""
    description = task.get("description", "")
    role = task.get("assigned_to_role", "AI")

    # ------------------------------------------------------------------
    # Decide on file extension based on simple heuristics
    # ------------------------------------------------------------------
    ext = "txt"
    if re.search(r"\b(python|script|code|\.py)\b", description, re.I):
        ext = "py"
    elif re.search(r"\bmarkdown|\.md\b", description, re.I):
        ext = "md"

    rel_path = f"completed_tasks/{task['id']}.{ext}"

    # ------------------------------------------------------------------
    # Build prompt for OpenAI to actually accomplish the task
    # ------------------------------------------------------------------
    prompt = (
        f"You are acting as the {role} of an early-stage startup. "
        f"Your task is: {description}\n\n"
        f"Please complete the task and output ONLY the deliverable content. "
        f"Do not include any explanations or commentary."
    )

    if openai_service.client:
        try:
            response = openai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            # If GPT wrapped output in code fences, strip them for file writes
            if ext in {"py", "txt", "md"} and content.startswith("```"):
                # Remove first and last triple backtick blocks
                parts = content.split("```")
                if len(parts) >= 3:
                    content = "```".join(parts[1:-1]).lstrip("python\n").lstrip()
        except Exception as exc:
            logger.error(f"OpenAI generation failed for task {task['id']}: {exc}")
            content = f"AUTO-GENERATED PLACEHOLDER FOR TASK: {description}"
    else:
        # Dev / offline mode – create placeholder
        content = f"AUTO-GENERATED PLACEHOLDER FOR TASK: {description}"

    return rel_path, content


async def _complete_task(task: Dict[str, Any]):
    """Generate deliverable for *task*, save it, and mark task completed."""
    task_id = task["id"]

    # Generate deliverable
    rel_path, content = await _infer_filename_and_content(task)
    abs_path = (WORKSPACE_ROOT / rel_path).resolve()
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(content)

    # Update task in DB/mock
    existing_resources = task.get("resources") or []
    if rel_path not in existing_resources:
        existing_resources.append(rel_path)

    await supabase_service.update_task(task_id, {"status": "completed", "resources": existing_resources})
    logger.info(f"Task {task_id} completed with deliverable {rel_path}")


async def task_completion_worker():
    """Background coroutine that auto-completes all pending tasks."""
    while True:
        try:
            pending = await _fetch_pending_tasks()
            if pending:
                logger.info(f"Auto-completing {len(pending)} pending task(s)…")
            for task in pending:
                await _complete_task(task)
        except Exception as exc:
            logger.exception(f"Background worker failure: {exc}")
        await asyncio.sleep(_POLL_INTERVAL_SEC) 