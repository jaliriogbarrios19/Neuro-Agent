from unittest.mock import patch
from src.agent.llm_provider import (
    OpenAIProvider, DeepSeekProvider, MistralProvider,
    QwenProvider, OpenRouterProvider, AnthropicProvider, create_provider,
)


class TestDeepSeekProvider:
    def test_init_reads_env(self):
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-ds", "DEEPSEEK_MODEL": "deepseek-v4-flash"}):
            p = DeepSeekProvider()
            assert p.api_key == "sk-ds"
            assert p.model == "deepseek-v4-flash"
            assert p.base_url == "https://api.deepseek.com"

    def test_default_model(self):
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-ds"}, clear=True):
            from src.agent.llm_provider import DeepSeekProvider as DP
            p = DP()
            assert p.model == "deepseek-v4-pro"


class TestMistralProvider:
    def test_init(self):
        with patch.dict("os.environ", {"MISTRAL_API_KEY": "sk-m", "MISTRAL_MODEL": "mistral-large-2512"}):
            p = MistralProvider()
            assert p.api_key == "sk-m"
            assert p.base_url == "https://api.mistral.ai/v1"


class TestQwenProvider:
    def test_init(self):
        with patch.dict("os.environ", {"QWEN_API_KEY": "sk-q", "QWEN_MODEL": "qwen3.7-max"}):
            p = QwenProvider()
            assert p.api_key == "sk-q"
            assert p.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"


class TestOpenRouterProvider:
    def test_init(self):
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or"}):
            p = OpenRouterProvider()
            assert p.base_url == "https://openrouter.ai/api/v1"


class TestCreateProvider:
    def test_default_is_deepseek(self):
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-ds"}):
            p = create_provider()
            assert isinstance(p, DeepSeekProvider)

    def test_explicit_openai(self):
        with patch.dict("os.environ", {"NEURO_PROVIDER": "openai", "OPENAI_API_KEY": "sk-o"}):
            p = create_provider()
            assert isinstance(p, OpenAIProvider)

    def test_explicit_anthropic(self):
        with patch.dict("os.environ", {"NEURO_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "sk-a"}):
            p = create_provider()
            assert isinstance(p, AnthropicProvider)
