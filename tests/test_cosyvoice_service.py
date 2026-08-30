import tempfile
import unittest
from pathlib import Path

from app.config import Settings
from app.cosyvoice_service import CosyVoiceService
from app.models import SpeechRequest


class CosyVoiceServiceTest(unittest.TestCase):
    def test_writes_mock_wav_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = CosyVoiceService(Settings(api_keys=[], storage_root=Path(temp_dir), enable_mock=True))
            path = service.synthesize(SpeechRequest(model="cosyvoice", input="hello"))

            self.assertTrue(path.is_file())
            self.assertEqual(".wav", path.suffix)

    def test_rejects_missing_command_when_mock_is_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = CosyVoiceService(Settings(api_keys=[], storage_root=Path(temp_dir), enable_mock=False))

            with self.assertRaises(RuntimeError):
                service.synthesize(SpeechRequest(model="cosyvoice", input="hello"))


if __name__ == "__main__":
    unittest.main()
