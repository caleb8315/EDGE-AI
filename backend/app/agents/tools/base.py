from __future__ import annotations

"""Base definitions for EDGE agent tools.

All concrete tools should inherit from `BaseTool` and implement the
`async run(**kwargs)` coroutine.  The class attributes `name` and
`description` are used by the agent framework (LangChain, CrewAI, etc.) to
expose the tool's capabilities.
"""

import abc
from typing import Any, Dict


class BaseTool(abc.ABC):
    """Abstract base class for all agent-accessible tools."""

    #: Unique tool identifier (snake_case)
    name: str = "base_tool"
    #: Short human-readable description (markdown allowed)
    description: str = "Abstract base tool – do not use directly."

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} name={self.name}>"

    # ---------------------------------------------------------------------
    # Core execution API
    # ---------------------------------------------------------------------

    @abc.abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:  # noqa: D401
        """Execute the tool.

        Concrete implementations should declare explicit parameters where
        possible to enable automatic argument validation and better DX.
        The method **must** be an ``async`` coroutine because it may involve
        IO-bound work (network requests, filesystem access, etc.).
        """

    # ------------------------------------------------------------------
    # Optional helper – synchronous fallback
    # ------------------------------------------------------------------

    def run_sync(self, *args: Any, **kwargs: Any) -> Any:
        """Synchronous wrapper that runs the async ``run`` method.

        This is handy when the calling context is not async-aware (e.g.,
        during quick unit tests).  **Never** call this from inside an event
        loop – it will block.
        """
        import asyncio

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.run(*args, **kwargs))
        finally:
            loop.close()

    # ------------------------------------------------------------------
    # OpenAI tools / function-calling helper
    # ------------------------------------------------------------------

    def openai_spec(self) -> dict:
        """Return a JSON-schema *tool* spec for OpenAI function calling.

        Each parameter is typed as string for simplicity; more specific
        schemas can be supplied by overriding this method in subclasses.
        """
        import inspect, json

        sig = inspect.signature(self.run)
        # Skip *args / **kwargs and "self"
        props = {}
        required = []
        for name, param in sig.parameters.items():
            if name == "self" or param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            props[name] = {
                "type": "string",
                "description": ("" if param.annotation is inspect.Parameter.empty else str(param.annotation)),
            }
            if param.default is inspect.Parameter.empty:
                required.append(name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        } 