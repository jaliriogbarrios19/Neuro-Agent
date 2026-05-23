from unittest.mock import AsyncMock, MagicMock, patch
from src.agent.agent import NeuroAgent


class FakeLLMProvider:
    name = "fake"

    def __init__(self, response_sequence: list[dict]):
        self.response_sequence = response_sequence
        self.call_count = 0

    async def chat(self, messages, tools=None):
        self.call_count += 1
        if self.call_count == 1:
            for event in self.response_sequence:
                yield event
        else:
            yield {"type": "token", "data": "Final answer"}
            yield {"type": "done"}


async def test_simple_message_no_tools():
    agent = NeuroAgent(vault_root="/tmp/test-vault")
    agent.llm = FakeLLMProvider([
        {"type": "token", "data": "Hello!"},
        {"type": "done"},
    ])

    events = []
    async for event in agent.process_message("Hi"):
        events.append(event)

    assert events[0] == {"type": "token", "data": "Hello!"}
    assert events[-1] == {"type": "done"}


async def test_message_with_tool_call():
    agent = NeuroAgent(vault_root="/tmp/test-vault")
    agent.llm = FakeLLMProvider([
        {"type": "token", "data": "Let me check..."},
        {"type": "tool_call", "id": "call_1", "name": "echo", "args": '{"text": "hi"}'},
        {"type": "done"},
    ])

    events = []
    async for event in agent.process_message("echo hello"):
        events.append(event)

    assert any(e["type"] == "tool_use" and e["tool"] == "echo" for e in events)
    assert events[-1] == {"type": "done"}


async def test_get_tool_schemas():
    agent = NeuroAgent(vault_root="/tmp/test-vault")
    schemas = agent.get_tool_schemas()
    names = [s["function"]["name"] for s in schemas]
    assert "echo" in names
    assert "read_file" in names
    assert all(s["type"] == "function" for s in schemas)
