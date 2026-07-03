"""SpeechService — decode an audio chunk and transcribe it."""

from __future__ import annotations

from app.domain.interfaces.speech import SpeechRecognizer
from app.domain.value_objects.speech import Transcript
from app.utils.media import decode_audio


class SpeechService:
    """Turns a base64 audio chunk into a :class:`Transcript`."""

    def __init__(self, recognizer: SpeechRecognizer) -> None:
        self._recognizer = recognizer

    async def listen(self, audio_b64: str | None) -> Transcript:
        audio = decode_audio(audio_b64)
        if not audio:
            return Transcript.empty()
        return await self._recognizer.transcribe(audio)
