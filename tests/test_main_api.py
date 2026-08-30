import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class MainApiTest(unittest.TestCase):
    def test_requires_bearer_token(self) -> None:
        client = TestClient(app)
        response = client.post("/v1/audio/speech", json={"model": "cosyvoice", "input": "hello"})

        self.assertEqual(401, response.status_code)

    def test_returns_audio_when_authorized(self) -> None:
        client = TestClient(app)

        with patch("app.main.service.synthesize") as synthesize:
            synthesize.return_value = Path(__file__)
            response = client.post(
                "/v1/audio/speech",
                headers={"Authorization": "Bearer local-dev-key"},
                json={"model": "cosyvoice", "input": "hello"},
            )

        self.assertEqual(200, response.status_code)


if __name__ == "__main__":
    unittest.main()
