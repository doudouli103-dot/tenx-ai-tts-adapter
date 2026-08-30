import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_keys: list[str]
    cosyvoice_command: str = ""
    storage_root: Path = Path("storage/audio")
    enable_mock: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        api_keys = [
            value.strip()
            for value in os.getenv("TENX_TTS_ADAPTER_API_KEYS", "local-dev-key").split(",")
            if value.strip()
        ]
        return cls(
            api_keys=api_keys,
            cosyvoice_command=os.getenv("COSYVOICE_COMMAND", ""),
            storage_root=Path(os.getenv("TTS_ADAPTER_STORAGE_ROOT", "storage/audio")),
            enable_mock=os.getenv("TTS_ADAPTER_ENABLE_MOCK", "false").lower() == "true",
        )
