from __future__ import annotations

"""LangChain-free tool agent using OpenAI function-calling.

This helper executes a single-turn conversation with automatic tool calls.
If the AI decides to call one of the registered tools, we run it and pass
its result back so the model can produce the final answer.
"""

from typing import List, Dict, Any
import json

from openai import AsyncOpenAI

from app.config import OPENAI_API_KEY
from .tools import ALL_TOOLS  # list of instantiated tools


class ToolAgent:
    """Lightweight wrapper around OpenAI function-calling + EDGE tools."""

    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.tools = ALL_TOOLS
        self._specs = [{"type": "function", "function": t.openai_spec()} for t in self.tools]
        self._tool_map = {t.name: t for t in self.tools}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(self, user_message: str, user_id: str | None = None) -> str:
        """Process *user_message* and return the assistant's answer."""
        system_content = (
            "You are EDGE, an autonomous startup co-founder AI with access to the user's uploaded codebase and documents. You have function-tools that can:\n"
            "• Explore the codebase (codebase_explorer): list files, analyze structure, search content, get project summaries\n"
            "• Read/write files in the workspace (file_manager)\n"
            "• Create tasks and attach resources (create_task)\n"
            "• Read PDFs and documents (read_pdf)\n"
            "• Search, scrape, summarize, send email, etc.\n\n"
            "CODEBASE ACCESS:\n"
            "- Use codebase_explorer to understand uploaded files before providing advice\n"
            "- Check what files are available with action='list' or action='summary'\n"
            "- Search for specific patterns/functions with action='search'\n"
            "- Read specific files with file_manager mode='read'\n\n"
            "ROLE-SPECIFIC GUIDANCE:\n"
            "• CTO: Focus on code architecture, technical debt, performance, security, and development practices\n"
            "• CMO: Analyze marketing materials, documentation, user-facing content, and growth strategies\n"
            "• CEO: Review business documents, strategic plans, and provide high-level guidance\n\n"
            "GPT Guidelines:\n"
            "1. When the user requests a deliverable (e.g., a plan, code, document), you **must** use the `create_task` tool. Set `status='completed'`, and provide the file content in `resource_content` and a descriptive file path in `resource_path`.\n"
            "2. In your final assistant reply, just reference the relative file path—do NOT output the full deliverable inline.\n"
            "3. If the user explicitly states which role should be assigned a task (e.g., 'tell the CTO to...'), you **must** set the 'assigned_to_role' parameter in the create_task call accordingly. Otherwise, infer the most appropriate role.\n"
            "4. Whenever the conversation identifies a follow-up or action item—**even if the user does NOT explicitly ask**—call `create_task` with a clear description, the appropriate `assigned_to_role`, and `status='pending'`.\n"
            "5. **ALWAYS** start by exploring the codebase with `codebase_explorer` if the user asks about code, architecture, or technical topics.\n"
            "6. If the deliverable is source code or a script, include the full code in `resource_content` and set `resource_path` with an appropriate filename and extension (e.g., `.py`, `.js`, `.ts`). Choose a sensible default language (Python) if the user does not specify one explicitly.\n"
        )
        system_content = system_content.replace("{uid}", user_id or "demo-user")

        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": user_message},
        ]

        # ------------------------------------------------------------------
        # 0. Heuristic: extract obvious action items directly from the user
        #    message so we can *guarantee* task creation even if the model
        #    fails to call `create_task`.  This is intentionally simple and
        #    should be refined over time.
        # ------------------------------------------------------------------
        async def _auto_create_tasks(raw: str) -> list[str]:
            """Detect phrases like 'need to <verb>' or 'update the X' and
            create pending tasks.  Returns human-readable summaries of any
            tasks we created so we can mention them in the assistant reply."""

            import re

            # Very naive extraction: split on ' and ', bullet markers, or new-lines
            candidates: list[str] = []
            for part in re.split(r"\band\b|[\n\u2022]", raw):
                part = part.strip(" .")
                if not part:
                    continue
                # Look for trigger phrases
                if re.search(r"\b(need to|should|must|have to|please)\b", part, re.I):
                    # remove leading trigger words for description
                    desc = re.sub(r"^(I|we)?\s*(need to|should|must|have to|please)\s*", "", part, flags=re.I).strip()
                    if desc:
                        candidates.append(desc[0].upper() + desc[1:])
                # Or imperative verb at start (update, gather, create, etc.)
                elif re.match(r"^(?:also\s+|then\s+)?(update|gather|create|build|write|design|implement|fix)\b", part, re.I):
                    candidates.append(part[0].upper() + part[1:])

            summaries: list[str] = []
            create_tool = self._tool_map.get("create_task")
            if not create_tool or not candidates:
                return summaries  # nothing to do

            # crude role inference helper
            def infer_role(desc: str) -> str:
                _d = desc.lower()
                if any(k in _d for k in ["ui", "interface", "frontend", "design"]):
                    return "CTO"
                if any(k in _d for k in ["marketing", "feedback", "survey", "campaign"]):
                    return "CMO"
                return "CEO"

            for desc in candidates:
                try:
                    await create_tool.run(
                        user_id=user_id,
                        assigned_to_role=infer_role(desc),
                        description=desc,
                        status="pending",
                    )
                    summaries.append(desc)
                except Exception:
                    # We swallow errors to avoid blocking the main chat flow
                    pass
            return summaries

        auto_tasks = await _auto_create_tasks(user_message)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._specs,
            tool_choice="auto",
        )
        choice = response.choices[0]
        if choice.finish_reason == "tool_calls":
            # Execute each requested tool (naïvely, sequentially)
            tool_outputs = {}
            for call in choice.message.tool_calls:
                # openai>=1.0: each call has .function with name & arguments
                name = getattr(call, "name", None)
                if name is None and hasattr(call, "function"):
                    name = call.function.name  # type: ignore
                    arguments_str = call.function.arguments  # type: ignore
                else:
                    arguments_str = call.arguments  # type: ignore

                args = json.loads(arguments_str or "{}")
                tool = self._tool_map.get(name)
                if not tool:
                    tool_outputs[name] = f"[Error] unknown tool {name}"
                    continue

                # Inject user_id if tool is create_task and arg missing
                if name == "create_task" and "user_id" not in args and user_id:
                    args["user_id"] = user_id

                # Inject auth_user_id for file_manager
                if name == "file_manager" and "auth_user_id" not in args and user_id:
                    args["auth_user_id"] = user_id

                # Inject auth_user_id for codebase_explorer
                if name == "codebase_explorer" and "auth_user_id" not in args and user_id:
                    args["auth_user_id"] = user_id

                try:
                    result = await tool.run(**args)
                except Exception as exc:  # pragma: no cover
                    result = f"[Tool execution error]: {exc}"
                tool_outputs[name] = result

            # Add the assistant tool call message and tool result message
            messages.append(choice.message)  # assistant with tool calls

            # For each tool call add a corresponding tool message
            for call in choice.message.tool_calls:
                call_id = getattr(call, "id", None)
                name = getattr(call, "name", None) or (call.function.name if hasattr(call, "function") else "")
                content = json.dumps({"result": tool_outputs.get(name, "")})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": content,
                    }
                )

            # Second completion – final answer
            response2 = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            final_answer = response2.choices[0].message.content.strip()
            if auto_tasks:
                bullets = "\n".join(f"• {t}" for t in auto_tasks)
                final_answer += f"\n\nI've added the following tasks:\n{bullets}"
            return final_answer

        # No tool call – just return content
        final_answer = choice.message.content.strip()
        if auto_tasks:
            bullets = "\n".join(f"• {t}" for t in auto_tasks)
            final_answer += f"\n\nI've added the following tasks:\n{bullets}"
        return final_answer


# Singleton instance (lazy)
_tool_agent: ToolAgent | None = None


def get_tool_agent() -> ToolAgent:
    global _tool_agent
    if _tool_agent is None:
        _tool_agent = ToolAgent()
    return _tool_agent 