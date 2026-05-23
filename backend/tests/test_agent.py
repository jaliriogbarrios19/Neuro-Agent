from src.agent.agent import NeuroAgent


async def test_agent_echo_tool():
    agent = NeuroAgent(vault_root="/tmp/neuro-vault-test")
    result = await agent.handle_message({"tool": "echo", "args": {"text": "hello"}})
    assert result["ok"] is True
    assert result["data"] == "hello"


async def test_agent_unknown_tool():
    agent = NeuroAgent(vault_root="/tmp/neuro-vault-test")
    result = await agent.handle_message({"tool": "nonexistent", "args": {}})
    assert result["ok"] is False
    assert "Unknown tool" in result["error"]


async def test_agent_default_memory_is_builtin():
    agent = NeuroAgent()
    assert agent.memory.name == "builtin"
