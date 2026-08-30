from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse

from app.config import Settings
from app.cosyvoice_service import CosyVoiceService
from app.models import SpeechRequest

settings = Settings.from_env()
service = CosyVoiceService(settings)
app = FastAPI(title="tenx-ai-tts-adapter", version="0.1.0")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/audio/speech")
async def speech(request: SpeechRequest, authorization: str | None = Header(default=None)) -> FileResponse:
    require_api_key(authorization)
    path = service.synthesize(request)
    media_type = "audio/mpeg" if path.suffix.lower() == ".mp3" else "audio/wav"
    return FileResponse(path, media_type=media_type, filename=path.name)


def require_api_key(authorization: str | None) -> None:
    if not settings.api_keys:
        return
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization[len("Bearer ") :].strip()
    if token not in settings.api_keys:
        raise HTTPException(status_code=403, detail="invalid bearer token")
