"""MemoryProvider abstract base class and built-in stub."""

from abc import ABC, abstractmethod


class MemoryProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def prefetch(self, query: str, session_id: str = "") -> str:
        ...

    @abstractmethod
    async def sync_turn(self, user: str, assistant: str, session_id: str = "") -> None:
        ...

    def system_prompt_block(self) -> str:
        return ""

    def get_tool_schemas(self) -> list[dict]:
        return []

    async def initialize(self, **kwargs) -> None:
        pass

    async def shutdown(self) -> None:
        pass


class BuiltinMemoryProvider(MemoryProvider):
    def __init__(self):
        super().__init__(name="builtin")

    async def prefetch(self, query: str, session_id: str = "") -> str:
        return ""

    async def sync_turn(self, user: str, assistant: str, session_id: str = "") -> None:
        pass
