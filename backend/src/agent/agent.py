"""Neuro Agent core — AI agent with tool dispatch and memory."""

import os

from src.agent.memory_provider import BuiltinMemoryProvider, MemoryProvider
from src.agent.tool_registry import ToolRegistry
from src.agent.tools.echo import handle_echo
from src.agent.tools.file_ops import list_directory, read_file, write_file


class NeuroAgent:
    def __init__(self, vault_root: str | None = None):
        self.registry = ToolRegistry()
        self.memory: MemoryProvider = BuiltinMemoryProvider()
        self.vault_root = vault_root or os.path.expanduser("~/neuro-vault")

        self.registry.register("echo", handle_echo)
        self.registry.register("read_file", self._file_handler(read_file))
        self.registry.register("write_file", self._file_handler(write_file))
        self.registry.register("list_directory", self._file_handler(list_directory))

    def set_memory_provider(self, provider: MemoryProvider) -> None:
        self.memory = provider

    async def handle_message(self, msg: dict) -> dict:
        tool = msg.get("tool")
        args = msg.get("args", {})
        if not tool:
            return {"ok": False, "error": "Missing 'tool' in message"}
        return await self.registry.dispatch(tool, args)

    def _file_handler(self, fn):
        from pathlib import Path

        vault = Path(self.vault_root)
        vault.mkdir(parents=True, exist_ok=True)

        async def handler(args):
            return await fn(args, vault_root=vault)

        return handler
