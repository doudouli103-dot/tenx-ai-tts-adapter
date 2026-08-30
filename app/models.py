from typing import Any

from pydantic import BaseModel, Field


class SpeechRequest(BaseModel):
    model: str = Field(min_length=1)
    input: str = Field(min_length=1)
    voice: str = "default"
    response_format: str = "wav"
    speed: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)
