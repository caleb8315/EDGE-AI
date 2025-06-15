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
            "You are EDGE, an autonomous startup co-founder.  You have function-tools that can:\n"
            "• write files to the workspace (file_manager).\n"
            "• create tasks and attach resources (create_task or tasks/{id}/resources).\n"
            "• scrape, search, summarize, send email, etc.\n\n"
            "GPT Guidelines:\n"
            "1. When the user requests a deliverable (plan, code, pdf, diagram, etc.) **always** use file_manager.write to save it under an appropriate path (no leading /).\n"
            "2. After saving, call create_task with user_id='{uid}', assigned_to_role set appropriately, status='completed', and resources=[PATH].\n"
            "3. In your final assistant reply, just reference the relative file path—do NOT output the full deliverable inline.\n"
        )
        system_content = system_content.replace("{uid}", user_id or "demo-user")

        messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": system_content,
            },
            {"role": "user", "content": user_message},
        ]

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
            return response2.choices[0].message.content.strip()

        # No tool call – just return content
        return choice.message.content.strip()


# Singleton instance (lazy)
_tool_agent: ToolAgent | None = None


def get_tool_agent() -> ToolAgent:
    global _tool_agent
    if _tool_agent is None:
        _tool_agent = ToolAgent()
    return _tool_agent 