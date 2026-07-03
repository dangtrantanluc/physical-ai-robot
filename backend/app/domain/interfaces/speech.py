"""Speech port.

Implementations live in ``app/infrastructure/speech`` (MockRecognizer today;
Whisper later). Business logic depends only on this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.value_objects.speech import Transcript


class SpeechRecognizer(ABC):
    """Transcribes raw audio bytes into text."""

    @abstractmethod
    async def transcribe(self, audio: bytes) -> Transcript:
        """Transcribe ``audio`` (implementation-defined encoding, e.g. WAV/PCM).

        Must return :meth:`Transcript.empty` for silent/empty input rather than
        raising.
        """
        raise NotImplementedError

    async def warmup(self) -> None:
        """Optional model pre-load. Default: no-op."""
        return None
