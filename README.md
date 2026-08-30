# tenx-ai-tts-adapter

OpenAI-compatible speech adapter for CosyVoice.

It exposes:

```text
POST /v1/audio/speech
```

Runtime boundary:

```text
video-agent
  -> tenx-ai-tts-adapter /v1/audio/speech
      -> CosyVoice
```

## Responsibility

`tenx-ai-tts-adapter` is the CosyVoice adapter. It converts an OpenAI-compatible speech request into a local CosyVoice command and returns audio bytes.

It does not route chat/image/video models, does not compose final videos, and does not store long-term business assets. Its generated files are temporary adapter outputs under `TTS_ADAPTER_STORAGE_ROOT`.

## Calling Chains

Inbound callers:

| Caller | Calls this adapter for | Endpoint |
| --- | --- | --- |
| `video-agent` | OpenAI-compatible speech generation | `/v1/audio/speech` |

Outbound dependencies:

| Dependency | Used for | Configuration |
| --- | --- | --- |
| CosyVoice | Real speech synthesis | `COSYVOICE_COMMAND` |
| Local disk | Temporary audio output before response streaming | `TTS_ADAPTER_STORAGE_ROOT` |

End-to-end speech chain:

```text
video-agent
  -> tenx-ai-tts-adapter /v1/audio/speech
      model=cosyvoice
      voice=default
      input=<narration text>
      -> COSYVOICE_COMMAND
          -> CosyVoice model
      -> returns audio/wav bytes
  -> video-agent saves storage/projects/<project_id>/audio/voice.wav
```

The recommended production mode is:

```text
TTS_ADAPTER_ENABLE_MOCK=false
COSYVOICE_COMMAND=<your CosyVoice CLI command>
```

Mock mode is only for testing the VideoAgent to TTS Adapter call chain before CosyVoice is installed.

## Configuration

```bash
export TENX_TTS_ADAPTER_API_KEYS=local-dev-key
export TTS_ADAPTER_STORAGE_ROOT=storage/audio
export COSYVOICE_COMMAND='python cosyvoice_cli.py --text {input} --voice {voice} --model {model} --output {output}'
```

For chain testing without CosyVoice installed:

```bash
export TTS_ADAPTER_ENABLE_MOCK=true
```

## Start

```bash
cd /Users/junweili1992163.com/ljwStudy/study-ai/tenx-ai-tts-adapter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 4030 --reload
```

## VideoAgent

Point `video-agent` to this adapter:

```bash
export TTS_ADAPTER_BASE_URL=http://127.0.0.1:4030/v1
export TTS_ADAPTER_API_KEY=local-dev-key
export VIDEO_AGENT_ENABLE_TTS_ADAPTER=true
```

Call this adapter directly:

```bash
curl -X POST http://127.0.0.1:4030/v1/audio/speech \
  -H 'Authorization: Bearer local-dev-key' \
  -H 'Content-Type: application/json' \
  --output voice.wav \
  -d '{
    "model": "cosyvoice",
    "input": "这是一段短视频旁白",
    "voice": "default",
    "response_format": "wav"
  }'
```

## Test

```bash
python -m unittest discover -s tests
```
