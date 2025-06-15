from __future__ import annotations

"""Tool: run_python

Execute short Python snippets and return stdout / result.  **Warning**: This
runs arbitrary code – in production you should sandbox or heavily restrict
it.  Here we evaluate in a `dict` namespace with selected built-ins.
"""

import io
import textwrap
from contextlib import redirect_stdout
from typing import Any, Dict

from .base import BaseTool


class RunPythonTool(BaseTool):
    name: str = "run_python"
    description: str = (
        "Execute a short Python script. Parameters:\n"
        "- code (str): The python code to execute.\n"
        "Returns: Captured stdout or repr(result) if variable `result` is set in the code."
    )

    async def run(self, code: str) -> str:  # type: ignore[override]
        # Dedent in case the code block is indented (common in markdown)
        code = textwrap.dedent(code)

        # Highly restricted globals – NO builtins except a safe subset
        allowed_builtins = {
            "print": print,
            "len": len,
            "range": range,
            "str": str,
            "int": int,
            "float": float,
            "dict": dict,
            "list": list,
            "set": set,
        }
        globals_dict: Dict[str, Any] = {"__builtins__": allowed_builtins}
        locals_dict: Dict[str, Any] = {}

        stdout = io.StringIO()
        try:
            with redirect_stdout(stdout):
                exec(code, globals_dict, locals_dict)
        except Exception as exc:  # pragma: no cover
            return f"[run_python] Error: {exc}"

        # If user set variable `result`, return it, else captured stdout
        if "result" in locals_dict:
            return repr(locals_dict["result"])
        return stdout.getvalue() or "<no output>" 