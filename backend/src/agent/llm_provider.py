"""LLM Provider abstraction — OpenAI, Anthropic, DeepSeek, Mistral, Qwen, OpenRouter."""

import json
import os
from abc import ABC, abstractmethod
from typing import AsyncGenerator

from dotenv import load_dotenv

from src.agent.models import DEEPSEEK_MODELS, MISTRAL_MODELS, QWEN_MODELS, MIMO_MODELS

load_dotenv()


class LLMProvider(ABC):
    name: str
    models: list[str] = []

    @abstractmethod
    async def chat(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncGenerator[dict, None]:
        ...


class OpenAICompatibleProvider(LLMProvider):
    """Base for providers using OpenAI-compatible API. Override base_url + env_prefix."""

    base_url: str = ""
    env_prefix: str = ""

    def __init__(self):
        self.api_key = os.getenv(f"{self.env_prefix}_API_KEY", "")
        self.model = os.getenv(f"{self.env_prefix}_MODEL", self.models[0] if self.models else "")

    async def chat(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> AsyncGenerator[dict, None]:
        if not self.api_key:
            raise ValueError(f"{self.env_prefix}_API_KEY not configured")

        from openai import AsyncOpenAI

        async with AsyncOpenAI(api_key=self.api_key, base_url=self.base_url) as client:
            kwargs: dict = {"model": self.model, "messages": messages, "stream": True}
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


class OpenAIProvider(OpenAICompatibleProvider):
    name = "openai"
    base_url = "https://api.openai.com/v1"
    env_prefix = "OPENAI"
    models = []  # No hardcoded list — use OPENAI_MODEL env var


class DeepSeekProvider(OpenAICompatibleProvider):
    name = "deepseek"
    base_url = "https://api.deepseek.com"
    env_prefix = "DEEPSEEK"
    models = DEEPSEEK_MODELS


class MistralProvider(OpenAICompatibleProvider):
    name = "mistral"
    base_url = "https://api.mistral.ai/v1"
    env_prefix = "MISTRAL"
    models = MISTRAL_MODELS


class QwenProvider(OpenAICompatibleProvider):
    name = "qwen"
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    env_prefix = "QWEN"
    models = QWEN_MODELS + MIMO_MODELS


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    base_url = "https://openrouter.ai/api/v1"
    env_prefix = "OPENROUTER"
    models = []  # Dynamically fetched


class OllamaProvider(OpenAICompatibleProvider):
    name = "ollama"
    base_url = "http://localhost:11434/v1"
    env_prefix = "OLLAMA"
    models = []

    def __init__(self):
        self.api_key = "ollama"  # Ollama doesn't require auth
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    models = []

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
        anthropic_messages = []
        for m in messages:
            if m["role"] == "system":
                system = str(m.get("content", ""))
            elif m["role"] == "assistant" and m.get("tool_calls"):
                blocks = []
                if m.get("content"):
                    blocks.append({"type": "text", "text": m["content"]})
                for tc in m["tool_calls"]:
                    args = json.loads(tc["function"]["arguments"]) if tc["function"]["arguments"] else {}
                    blocks.append({"type": "tool_use", "id": tc["id"], "name": tc["function"]["name"], "input": args})
                anthropic_messages.append({"role": "assistant", "content": blocks})
            elif m["role"] == "tool":
                anthropic_messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": str(m["content"])}]})
            else:
                anthropic_messages.append(m)

        kwargs: dict = {"model": self.model, "max_tokens": 4096, "messages": anthropic_messages, "stream": True}
        if system:
            kwargs["system"] = system

        if tools:
            kwargs["tools"] = [
                {"name": t["function"]["name"], "description": t["function"].get("description", ""),
                 "input_schema": t["function"]["parameters"]}
                for t in tools
            ]

        async with client.messages.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        yield {"type": "token", "data": event.delta.text}
                elif event.type == "content_block_stop":
                    if hasattr(event, "content_block") and event.content_block.type == "tool_use":
                        cb = event.content_block
                        yield {"type": "tool_call", "id": cb.id, "name": cb.name, "args": json.dumps(cb.input)}

        yield {"type": "done"}


_PROVIDER_MAP: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "deepseek": DeepSeekProvider,
    "mistral": MistralProvider,
    "qwen": QwenProvider,
    "openrouter": OpenRouterProvider,
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
}


def create_provider() -> LLMProvider:
    name = os.getenv("NEURO_PROVIDER", "deepseek").strip().lower()
    cls = _PROVIDER_MAP.get(name, DeepSeekProvider)
    return cls()
