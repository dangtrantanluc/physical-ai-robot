"""MockRecognizer — a stand-in for a real speech-to-text model.

Real STT can't be faked meaningfully, so for development/testing this recognizer
treats the incoming ``audio`` bytes as UTF-8 *text*: send base64("follow me") and it
transcribes to "follow me". Non-text (real audio) bytes yield an empty transcript.

This keeps the voice-command path testable end-to-end. Swap for Whisper by
implementing :class:`SpeechRecognizer` and setting ``SPEECH_RECOGNIZER=whisper`` —
the planner and behaviors are unaffected.
"""

from __future__ import annotations

from app.domain.interfaces.speech import SpeechRecognizer
from app.domain.value_objects.speech import Transcript

# A plausible transcript from raw text bytes shouldn't be longer than this.
_MAX_TEXT_LEN = 256


class MockRecognizer(SpeechRecognizer):
    """Interprets audio bytes as UTF-8 text for development."""

    async def transcribe(self, audio: bytes) -> Transcript:
        if not audio:
            return Transcript.empty()
        try:
            text = audio.decode("utf-8").strip()
        except UnicodeDecodeError:
            # Real audio payload — a mock can't transcribe it.
            return Transcript.empty()
        if not text or len(text) > _MAX_TEXT_LEN or not text.isprintable():
            return Transcript.empty()
        return Transcript(text=text.lower(), confidence=0.95, language="und")
