"""Speech value objects — the output of the speech-recognition subsystem."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Transcript:
    """A recognized utterance.

    Attributes:
        text: recognized text (lower-cased, trimmed by convention).
        confidence: recognizer confidence in ``[0, 1]``.
        language: BCP-47 language tag if known (e.g. ``vi``, ``en``).
    """

    text: str = ""
    confidence: float = 0.0
    language: str | None = None

    @classmethod
    def empty(cls) -> Transcript:
        return cls()

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()
