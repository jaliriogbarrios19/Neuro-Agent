"""LLM model catalogs — current models per provider as of May 2026."""

DEEPSEEK_MODELS = [
    "deepseek-v4-pro",
    "deepseek-v4-flash",
]

MISTRAL_MODELS = [
    "mistral-medium-3-5",
    "mistral-small-2603",
    "mistral-large-2512",
    "devstral-2512",
    "ministral-14b-2512",
]

QWEN_MODELS = [
    "qwen3.7-max",
    "qwen3.7-max-2026-05-20",
    "qwen3.6-plus",
    "qwen3.6-flash",
    "qwen3.6-max-preview",
]

MIMO_MODELS = [
    "mimo-v2.5-pro",
]

OPENROUTER_DEFAULT_MODELS = [
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-v4-flash",
    "openai/gpt-5.4",
    "openai/gpt-4.1",
    "anthropic/claude-sonnet-4-20250514",
    "anthropic/claude-opus-4-20250514",
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "meta-llama/llama-4-maverick",
    "qwen/qwen3.7-max",
    "mistral/mistral-large-2512",
]


def get_all_models() -> dict[str, list[str]]:
    return {
        "deepseek": DEEPSEEK_MODELS,
        "mistral": MISTRAL_MODELS,
        "qwen": QWEN_MODELS + MIMO_MODELS,
        "openrouter": OPENROUTER_DEFAULT_MODELS,
    }
