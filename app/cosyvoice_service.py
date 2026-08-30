import shlex
import subprocess
import wave
from pathlib import Path
from uuid import uuid4

from app.config import Settings
from app.models import SpeechRequest


class CosyVoiceService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def synthesize(self, request: SpeechRequest) -> Path:
        output_path = self.output_path(request.response_format)
        if self.settings.cosyvoice_command:
            self.run_command(request, output_path)
            return output_path
        if self.settings.enable_mock:
            self.write_mock_wav(output_path)
            return output_path
        raise RuntimeError("COSYVOICE_COMMAND is not configured")

    def output_path(self, response_format: str) -> Path:
        extension = response_format.lower().strip(".") or "wav"
        if extension not in {"wav", "mp3"}:
            extension = "wav"
        self.settings.storage_root.mkdir(parents=True, exist_ok=True)
        return self.settings.storage_root / f"{uuid4()}.{extension}"

    def run_command(self, request: SpeechRequest, output_path: Path) -> None:
        command = self.settings.cosyvoice_command.format(
            input=shlex.quote(request.input),
            output=shlex.quote(str(output_path)),
            voice=shlex.quote(request.voice),
            model=shlex.quote(request.model),
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "CosyVoice command failed")
        if not output_path.is_file():
            raise RuntimeError("CosyVoice command completed but did not create output audio")

    def write_mock_wav(self, output_path: Path) -> None:
        with wave.open(str(output_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00\x00" * 16000)
