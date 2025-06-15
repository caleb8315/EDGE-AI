from __future__ import annotations

"""Tool: calendar_tool

Placeholder interface for Google Calendar operations (create event, list events).
Requires OAuth2 credentials which are **not** configured yet.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from .base import BaseTool


class CalendarTool(BaseTool):
    name: str = "calendar_tool"
    description: str = (
        "Interact with Google Calendar. Parameters vary by mode:\n"
        "- mode (str): 'create' or 'list'.\n"
        "- For create: title, start_time (ISO), duration_minutes (int).\n"
        "- For list: date (YYYY-MM-DD).\n"
        "Returns: Details about the created event or events on a given day.  (Stub implementation.)"
    )

    async def run(
        self,
        mode: str,
        *,
        title: Optional[str] = None,
        start_time: Optional[str] = None,
        duration_minutes: int = 60,
        date: Optional[str] = None,
    ) -> str:  # type: ignore[override]
        # Stub – real implementation would use google-api-python-client + OAuth2
        if mode == "create":
            return (
                f"[calendar_tool stub] Would create event '{title}' at {start_time} "
                f"for {duration_minutes} minutes."
            )
        elif mode == "list":
            return f"[calendar_tool stub] Would list events on {date}."
        else:
            raise ValueError("mode must be 'create' or 'list'") 