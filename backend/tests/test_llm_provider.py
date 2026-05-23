from unittest.mock import AsyncMock, patch
from src.agent.llm_provider import OpenAIProvider, AnthropicProvider, create_provider


class TestOpenAIProvider:
    def test_init_reads_env_vars(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test", "OPENAI_MODEL": "gpt-4.1-mini"}):
            provider = OpenAIProvider()
            assert provider.api_key == "sk-test"
            assert provider.model == "gpt-4.1-mini"

    def test_missing_api_key_raises(self):
        provider = OpenAIProvider()
        provider.api_key = ""


class TestAnthropicProvider:
    def test_init_reads_env_vars(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "ant-test", "ANTHROPIC_MODEL": "claude-opus-4"}):
            provider = AnthropicProvider()
            assert provider.api_key == "ant-test"
            assert provider.model == "claude-opus-4"


class TestCreateProvider:
    def test_default_to_openai(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("os.getenv", side_effect=lambda k, d=None: d):
                provider = create_provider()
                assert isinstance(provider, OpenAIProvider)

    def test_explicit_anthropic(self):
        with patch.dict("os.environ", {"NEURO_PROVIDER": "anthropic"}):
            provider = create_provider()
            assert isinstance(provider, AnthropicProvider)
