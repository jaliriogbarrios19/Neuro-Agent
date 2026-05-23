from src.agent.memory_provider import MemoryProvider, BuiltinMemoryProvider


class CountingProvider(MemoryProvider):
    def __init__(self):
        super().__init__(name="test-counter")
        self.prefetch_count = 0
        self.sync_count = 0

    async def prefetch(self, query: str, session_id: str = "") -> str:
        self.prefetch_count += 1
        return f"prefetch:{query}"

    async def sync_turn(self, user: str, assistant: str, session_id: str = "") -> None:
        self.sync_count += 1


async def test_builtin_provider_prefetch_returns_empty():
    provider = BuiltinMemoryProvider()
    result = await provider.prefetch("test query")
    assert result == ""


async def test_builtin_provider_sync_turn_does_not_raise():
    provider = BuiltinMemoryProvider()
    await provider.sync_turn("hello", "world")


async def test_custom_provider_prefetch_returns_data():
    provider = CountingProvider()
    result = await provider.prefetch("hello")
    assert result == "prefetch:hello"
    assert provider.prefetch_count == 1


async def test_custom_provider_sync_turn_increments_counter():
    provider = CountingProvider()
    await provider.sync_turn("user msg", "assistant msg")
    assert provider.sync_count == 1
