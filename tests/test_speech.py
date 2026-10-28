"""Tests S2: speech providers, factory, config — χωρίς δίκτυο ή μικρόφωνο."""
from pathlib import Path

from tooldock.core.config import Config
from tooldock.speech.base import STTProvider
from tooldock.speech.factory import create_provider
from tooldock.speech.google_web import GoogleWebSpeechProvider
from tooldock.speech.whisper_local import FasterWhisperProvider


class DummyProvider(STTProvider):
    name = "dummy"

    def transcribe(self, audio_path: Path, language: str) -> str:
        return "δοκιμή"


def test_config_defaults(tmp_path: Path) -> None:
    config = Config(tmp_path / "config.json")
    assert config.get("speech.provider") == "google"
    assert config.get("speech.language") == "el-GR"
    assert config.get("speech.whisper.model") == "small"


def test_factory_google(tmp_path: Path) -> None:
    config = Config(tmp_path / "config.json")
    provider = create_provider(config)
    assert isinstance(provider, GoogleWebSpeechProvider)


def test_factory_whisper(tmp_path: Path) -> None:
    config = Config(tmp_path / "config.json")
    config.set("speech.provider", "whisper")
    provider = create_provider(config)
    assert isinstance(provider, FasterWhisperProvider)


def test_dummy_provider(tmp_path: Path) -> None:
    provider = DummyProvider()
    assert provider.transcribe(tmp_path / "a.wav", "el-GR") == "δοκιμή"
    assert provider.available() is True
