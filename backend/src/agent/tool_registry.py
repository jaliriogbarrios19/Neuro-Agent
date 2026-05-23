"""Tool registry — maps tool names to async handler functions."""

from typing import Any, Callable, Coroutine

Handler = Callable[[dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Handler] = {}

    def register(self, name: str, handler: Handler) -> None:
        self._tools[name] = handler

    async def dispatch(self, tool: str, args: dict[str, Any]) -> dict[str, Any]:
        handler = self._tools.get(tool)
        if handler is None:
            return {"ok": False, "error": f"Unknown tool: {tool}"}
        try:
            return await handler(args)
        except Exception as e:
            return {"ok": False, "error": str(e)}
