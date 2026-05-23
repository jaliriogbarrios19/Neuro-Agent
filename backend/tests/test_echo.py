from src.agent.tools.echo import handle_echo


async def test_echo_returns_input_verbatim():
    result = await handle_echo({"text": "hello world"})
    assert result["ok"] is True
    assert result["data"] == "hello world"


async def test_echo_empty_text():
    result = await handle_echo({"text": ""})
    assert result["ok"] is True
    assert result["data"] == ""


async def test_echo_missing_text_key():
    result = await handle_echo({})
    assert result["ok"] is False
    assert "error" in result
    assert "text" in result["error"]
