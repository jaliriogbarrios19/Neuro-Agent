"""Audio Transcription — Deepgram, AssemblyAI, and Gladia providers."""

import asyncio
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Utterance:
    speaker: str
    text: str
    start: float = 0.0
    end: float = 0.0


@dataclass
class Transcript:
    text: str
    utterances: list[Utterance]
    language: str = ""
    provider: str = ""


class TranscriptionProvider(ABC):
    name: str

    @abstractmethod
    async def transcribe(self, file_path: str, language: str = "en") -> Transcript:
        ...


class DeepgramProvider(TranscriptionProvider):
    name = "deepgram"

    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY", "")

    async def transcribe(self, file_path: str, language: str = "en") -> Transcript:
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY not configured")

        import httpx

        url = f"https://api.deepgram.com/v1/listen?diarize=true&language={language}"
        headers = {"Authorization": f"Token {self.api_key}", "Content-Type": "audio/*"}

        async with httpx.AsyncClient(timeout=120) as client:
            with open(file_path, "rb") as f:
                resp = await client.post(url, headers=headers, content=f.read())
            resp.raise_for_status()
            data = resp.json()

        result = data.get("results", {}).get("channels", [{}])[0]
        alternatives = result.get("alternatives", [{}])[0]

        utterances = []
        words = alternatives.get("words", [])
        current_speaker = None
        current_text = []
        current_start = 0.0

        for w in words:
            speaker = f"Speaker {w.get('speaker', 0)}"
            if speaker != current_speaker:
                if current_text:
                    utterances.append(Utterance(speaker=current_speaker, text=" ".join(current_text), start=current_start, end=w.get("end", 0)))
                current_speaker = speaker
                current_text = [w.get("word", "")]
                current_start = w.get("start", 0)
            else:
                current_text.append(w.get("word", ""))

        if current_text:
            utterances.append(Utterance(speaker=current_speaker, text=" ".join(current_text), start=current_start, end=words[-1].get("end", 0) if words else 0))

        full_text = alternatives.get("transcript", "")
        return Transcript(text=full_text, utterances=utterances, language=language, provider="deepgram")


class AssemblyAIProvider(TranscriptionProvider):
    name = "assemblyai"

    def __init__(self):
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY", "")

    async def transcribe(self, file_path: str, language: str = "en") -> Transcript:
        if not self.api_key:
            raise ValueError("ASSEMBLYAI_API_KEY not configured")

        import httpx

        headers = {"authorization": self.api_key}
        async with httpx.AsyncClient(timeout=120) as client:
            with open(file_path, "rb") as f:
                upload_resp = await client.post("https://api.assemblyai.com/v2/upload", headers=headers, content=f.read())
            upload_resp.raise_for_status()
            upload_url = upload_resp.json()["upload_url"]

            submit_resp = await client.post(
                "https://api.assemblyai.com/v2/transcript",
                json={"audio_url": upload_url, "speaker_labels": True, "language_code": language},
                headers=headers,
            )
            submit_resp.raise_for_status()
            transcript_id = submit_resp.json()["id"]

            for _ in range(60):
                poll_resp = await client.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
                poll_resp.raise_for_status()
                status_data = poll_resp.json()
                if status_data["status"] == "completed":
                    break
                if status_data["status"] == "error":
                    raise RuntimeError(f"AssemblyAI error: {status_data.get('error', 'unknown')}")
                await asyncio.sleep(2)
            else:
                raise TimeoutError("AssemblyAI transcription timed out")

        utterances = []
        for u in status_data.get("utterances", []):
            utterances.append(Utterance(speaker=f"Speaker {u['speaker']}", text=u["text"], start=u["start"] / 1000, end=u["end"] / 1000))

        return Transcript(text=status_data.get("text", ""), utterances=utterances, language=language, provider="assemblyai")


class GladiaProvider(TranscriptionProvider):
    name = "gladia"

    def __init__(self):
        self.api_key = os.getenv("GLADIA_API_KEY", "")

    async def transcribe(self, file_path: str, language: str = "en") -> Transcript:
        if not self.api_key:
            raise ValueError("GLADIA_API_KEY not configured")

        import httpx

        headers = {"x-gladia-key": self.api_key}
        async with httpx.AsyncClient(timeout=120) as client:
            with open(file_path, "rb") as f:
                files = {"audio": (Path(file_path).name, f, "audio/*")}
                resp = await client.post(
                    "https://api.gladia.io/v2/transcription",
                    headers=headers,
                    files=files,
                    data={"language": language, "diarization": "true"},
                )
            resp.raise_for_status()
            data = resp.json()

        result = data.get("result", {})
        utterances = []
        for u in result.get("transcription", {}).get("utterances", []):
            utterances.append(Utterance(speaker=f"Speaker {u.get('speaker', 0)}", text=u.get("text", ""), start=u.get("start", 0), end=u.get("end", 0)))

        full_text = result.get("transcription", {}).get("full_transcript", "")
        return Transcript(text=full_text, utterances=utterances, language=language, provider="gladia")


def create_transcription_provider() -> TranscriptionProvider:
    name = os.getenv("TRANSCRIPTION_PROVIDER", "deepgram").strip().lower()
    if name == "assemblyai":
        return AssemblyAIProvider()
    if name == "gladia":
        return GladiaProvider()
    return DeepgramProvider()
