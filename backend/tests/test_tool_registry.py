from src.agent.tool_registry import ToolRegistry


async def test_register_and_dispatch_echo():
    registry = ToolRegistry()

    async def echo_handler(args):
        return {"ok": True, "data": args["text"]}

    registry.register("echo", echo_handler)
    result = await registry.dispatch("echo", {"text": "hello"})
    assert result == {"ok": True, "data": "hello"}


async def test_dispatch_unknown_tool_returns_error():
    registry = ToolRegistry()
    result = await registry.dispatch("unknown", {})
    assert result["ok"] is False
    assert "Unknown tool" in result["error"]


async def test_register_duplicate_overwrites():
    registry = ToolRegistry()

    async def first(args):
        return "first"

    async def second(args):
        return "second"

    registry.register("echo", first)
    registry.register("echo", second)
    result = await registry.dispatch("echo", {})
    assert result == "second"
