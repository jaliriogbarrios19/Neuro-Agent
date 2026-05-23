"""LLM Provider abstraction — OpenAI and Anthropic adapters with streaming."""

import json
import os
from abc import ABC, abstractmethod
from typing import AsyncGenerator

from dotenv import load_dotenv

load_dotenv()


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def chat(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncGenerator[dict, None]:
        ...


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    async def chat(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncGenerator[dict, None]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools

        stream = await client.chat.completions.create(**kwargs)

        current_tool_call = None
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta is None:
                continue

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.id:
                        current_tool_call = {"id": tc.id, "name": tc.function.name or "", "args": ""}
                    if tc.function and tc.function.arguments and current_tool_call:
                        current_tool_call["args"] += tc.function.arguments

            if delta.content:
                yield {"type": "token", "data": delta.content}

        if current_tool_call:
            yield {"type": "tool_call", **current_tool_call}

        yield {"type": "done"}


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    async def chat(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncGenerator[dict, None]:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=self.api_key)

        system = ""
        filtered = []
        for m in messages:
            if m["role"] == "system":
                system = str(m.get("content", ""))
            else:
                filtered.append(m)

        kwargs: dict = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": filtered,
            "stream": True,
        }
        if system:
            kwargs["system"] = system

        anthropic_tools = None
        if tools:
            anthropic_tools = [
                {"name": t["function"]["name"], "description": t["function"].get("description", ""),
                 "input_schema": t["function"]["parameters"]}
                for t in tools
            ]
            kwargs["tools"] = anthropic_tools

        async with client.messages.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        yield {"type": "token", "data": event.delta.text}
                    elif event.delta.type == "input_json_delta":
                        pass  # accumulated in content_block_stop
                elif event.type == "content_block_stop":
                    if hasattr(event, "content_block") and event.content_block.type == "tool_use":
                        cb = event.content_block
                        yield {"type": "tool_call", "id": cb.id, "name": cb.name, "args": json.dumps(cb.input)}

            final = await stream.get_final_message()
            for block in final.content:
                if block.type == "tool_use" and not any(
                    True for _ in []  # already yielded via content_block_stop
                ):
                    pass

        yield {"type": "done"}


def create_provider() -> LLMProvider:
    name = os.getenv("NEURO_PROVIDER", "openai").strip().lower()
    if name == "anthropic":
        return AnthropicProvider()
    return OpenAIProvider()
