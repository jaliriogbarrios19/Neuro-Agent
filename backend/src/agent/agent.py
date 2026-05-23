"""Neuro Agent core — AI agent with LLM, tool dispatch, and memory."""

import json
import os
from typing import AsyncGenerator

from src.agent.llm_provider import LLMProvider, create_provider
from src.agent.memory_provider import BuiltinMemoryProvider, MemoryProvider
from src.agent.tool_registry import ToolRegistry
from src.agent.tools.echo import handle_echo
from src.agent.tools.file_ops import list_directory, read_file, write_file
from src.research.synthesis import deep_research
from src.transcription.provider import create_transcription_provider

MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = """You are Neuro Agent, an AI assistant integrated into a knowledge management desktop app.
You help users with notes, files, research, and coding tasks.
When users ask about files, use the available tools. Be concise and helpful."""


class NeuroAgent:
    def __init__(self, vault_root: str | None = None):
        self.registry = ToolRegistry()
        self.memory: MemoryProvider = BuiltinMemoryProvider()
        self.llm: LLMProvider = create_provider()
        self.vault_root = vault_root or os.path.expanduser("~/neuro-vault")

        self.registry.register("echo", handle_echo)
        self.registry.register("read_file", self._file_handler(read_file))
        self.registry.register("write_file", self._file_handler(write_file))
        self.registry.register("list_directory", self._file_handler(list_directory))
        self.registry.register("deep_research", self._research_handler)
        self.registry.register("transcribe_audio", self._transcription_handler)

    def set_memory_provider(self, provider: MemoryProvider) -> None:
        self.memory = provider

    def get_tool_schemas(self) -> list[dict]:
        schemas = []
        for name, handler in self.registry._tools.items():
            doc = (handler.__doc__ or name).strip()
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": doc,
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            })
        return schemas

    async def process_message(self, text: str) -> AsyncGenerator[dict, None]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        tools = self.get_tool_schemas()

        for iteration in range(MAX_TOOL_ITERATIONS):
            tool_calls = []

            async for event in self.llm.chat(messages, tools if tools else None):
                if event["type"] == "token":
                    yield event
                elif event["type"] == "tool_call":
                    tool_calls.append(event)
                elif event["type"] == "done":
                    pass

            if not tool_calls:
                yield {"type": "done"}
                return

            assistant_content: list[dict] = []
            for tc in tool_calls:
                result = await self.registry.dispatch(tc["name"], json.loads(tc["args"]) if tc["args"] else {})
                yield {"type": "tool_use", "tool": tc["name"], "args": tc["args"], "result": result}
                tool_response = json.dumps(result) if isinstance(result, dict) else str(result)
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tc["id"],
                        "type": "function",
                        "function": {"name": tc["name"], "arguments": tc["args"]},
                    }],
                })
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": tool_response})

        yield {"type": "error", "data": "Max tool iterations reached"}

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

    async def _research_handler(self, args: dict) -> dict:
        query = args.get("query", "")
        depth = args.get("depth", "standard")
        if not query:
            return {"ok": False, "error": "Missing 'query' for deep_research"}

        chat_fn = self.llm.chat if hasattr(self, "llm") else None
        brief = await deep_research(query, llm_chat=chat_fn, depth=depth)
        return {
            "ok": True,
            "data": {
                "question": brief.question,
                "summary": brief.summary,
                "papers_found": len(brief.papers),
                "references": brief.references[:10],
            },
        }

    async def _transcription_handler(self, args: dict) -> dict:
        file_path = args.get("file_path", "")
        language = args.get("language", "en")
        if not file_path:
            return {"ok": False, "error": "Missing 'file_path' for transcribe_audio"}

        provider = create_transcription_provider()
        transcript = await provider.transcribe(file_path, language)
        return {
            "ok": True,
            "data": {
                "text": transcript.text,
                "utterances": [{"speaker": u.speaker, "text": u.text, "start": u.start, "end": u.end} for u in transcript.utterances],
                "language": transcript.language,
                "provider": transcript.provider,
            },
        }
