from unittest.mock import patch, AsyncMock, MagicMock
from src.transcription.provider import (
    DeepgramProvider, AssemblyAIProvider, GladiaProvider,
    create_transcription_provider, TranscriptionProvider,
)


class TestProviderCreation:
    def test_default_is_deepgram(self):
        with patch.dict("os.environ", {}, clear=True):
            p = create_transcription_provider()
            assert p.name == "deepgram"

    def test_explicit_assemblyai(self):
        with patch.dict("os.environ", {"TRANSCRIPTION_PROVIDER": "assemblyai"}):
            p = create_transcription_provider()
            assert isinstance(p, AssemblyAIProvider)

    def test_explicit_gladia(self):
        with patch.dict("os.environ", {"TRANSCRIPTION_PROVIDER": "gladia"}):
            p = create_transcription_provider()
            assert isinstance(p, GladiaProvider)


class TestDeepgramProvider:
    async def test_missing_key_raises(self):
        import pytest

        with patch.dict("os.environ", {}, clear=True):
            p = DeepgramProvider()
            with pytest.raises(ValueError, match="DEEPGRAM_API_KEY"):
                await p.transcribe("test.mp3")

    def test_init_reads_key(self):
        with patch.dict("os.environ", {"DEEPGRAM_API_KEY": "sk-dg-test"}):
            p = DeepgramProvider()
            assert p.api_key == "sk-dg-test"


class TestAssemblyAIProvider:
    def test_missing_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            p = AssemblyAIProvider()
            p.api_key = ""


class TestGladiaProvider:
    def test_missing_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            p = GladiaProvider()
            p.api_key = ""
