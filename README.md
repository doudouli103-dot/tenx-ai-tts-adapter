# tenx-ai-tts-adapter

OpenAI-compatible speech adapter for CosyVoice.

Recommended production target:

```text
Mac Studio
  tenx-ai-tts-adapter:4030
      -> CosyVoice2-0.5B

Windows / video-agent machine
  video-agent
      -> http://<Mac-Studio-IP>:4030/v1/audio/speech
```

It exposes:

```text
POST /v1/audio/speech
```

Default local port:

```text
http://127.0.0.1:4030
```

Runtime boundary:

```text
video-agent
  -> tenx-ai-tts-adapter /v1/audio/speech
      -> CosyVoice
```

This service is intentionally separate from `tenx-ai-gateway`. `video-agent` calls it directly, so the Gateway remains focused on text/image/video model routing.

## Responsibility

`tenx-ai-tts-adapter` is the CosyVoice adapter. It converts an OpenAI-compatible speech request into a local CosyVoice command and returns audio bytes.

It does not route chat/image/video models, does not compose final videos, and does not store long-term business assets. Its generated files are temporary adapter outputs under `TTS_ADAPTER_STORAGE_ROOT`.

It is intentionally not behind `tenx-ai-gateway`. `video-agent` calls this adapter directly so the Gateway remains independent.

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

Storage behavior:

```text
TTS_ADAPTER_STORAGE_ROOT/
  <uuid>.wav
```

The adapter writes a temporary audio file, returns its bytes to `video-agent`, and `video-agent` stores the project copy under `storage/projects/<project_id>/audio/voice.wav`.

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

## Recommended Model

Use `CosyVoice2-0.5B` as the first production TTS model.

| Model | When to use | Notes |
| --- | --- | --- |
| `CosyVoice2-0.5B` | Primary choice for `video-agent` narration | Good quality and stable enough for short-video voiceover. |
| Kokoro MLX | Lightweight local fallback | Useful for quick experiments, but not the main target here. |
| Fish Speech | Later advanced voice cloning | Keep for a future high-quality voice-clone track. |

Recommended model placement:

```text
Mac Studio
  ~/ai/CosyVoice
  ~/ai/CosyVoice/pretrained_models/CosyVoice2-0.5B
  /Users/junweili1992163.com/ljwStudy/study-ai/tenx-ai-tts-adapter
```

## Production Mode

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

Supported `COSYVOICE_COMMAND` placeholders:

| Placeholder | Meaning |
| --- | --- |
| `{input}` | Text to synthesize, shell-quoted by the adapter. |
| `{output}` | Target audio path, shell-quoted by the adapter. |
| `{voice}` | Voice name from request body, shell-quoted by the adapter. |
| `{model}` | Model name from request body, shell-quoted by the adapter. |

The command must create the file at `{output}`. If the command exits successfully but the file is missing, the adapter returns an error.

For chain testing without CosyVoice installed:

```bash
export TTS_ADAPTER_ENABLE_MOCK=true
```

## Install CosyVoice2-0.5B On Mac Studio

Create the runtime directory:

```bash
mkdir -p ~/ai
cd ~/ai
```

Clone CosyVoice:

```bash
git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice
```

Create a Python environment for CosyVoice:

```bash
conda create -n cosyvoice -y python=3.10
conda activate cosyvoice
pip install -r requirements.txt
pip install huggingface_hub
```

Download `CosyVoice2-0.5B`:

```bash
python - <<'PY'
from huggingface_hub import snapshot_download

snapshot_download(
    "FunAudioLLM/CosyVoice2-0.5B",
    local_dir="pretrained_models/CosyVoice2-0.5B",
    local_dir_use_symlinks=False,
)
PY
```

After download, the model should exist here:

```text
~/ai/CosyVoice/pretrained_models/CosyVoice2-0.5B
```

## CosyVoice CLI Wrapper

`tenx-ai-tts-adapter` expects a command-line entry point that accepts text and writes a wav file. If your CosyVoice checkout does not already provide a suitable CLI, add a small wrapper script in the CosyVoice project and point `COSYVOICE_COMMAND` to it.

Example command shape:

```bash
export COSYVOICE_COMMAND='conda run -n cosyvoice python ~/ai/CosyVoice/tools/cosyvoice_cli.py --model_dir ~/ai/CosyVoice/pretrained_models/CosyVoice2-0.5B --text {input} --voice {voice} --output {output}'
```

The exact wrapper implementation depends on the CosyVoice runtime API you choose, but the adapter contract stays the same:

```text
stdin:  not required
input:  --text <text>
voice:  --voice <voice>
output: --output <wav path>
result: command creates <wav path>
```

## Start

Start the adapter on Mac Studio:

```bash
cd /Users/junweili1992163.com/ljwStudy/study-ai/tenx-ai-tts-adapter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export TENX_TTS_ADAPTER_API_KEYS=local-dev-key
export TTS_ADAPTER_STORAGE_ROOT=storage/audio
export TTS_ADAPTER_ENABLE_MOCK=false
export COSYVOICE_COMMAND='conda run -n cosyvoice python ~/ai/CosyVoice/tools/cosyvoice_cli.py --model_dir ~/ai/CosyVoice/pretrained_models/CosyVoice2-0.5B --text {input} --voice {voice} --output {output}'

uvicorn app.main:app --host 0.0.0.0 --port 4030 --reload
```

Health check:

```bash
curl http://127.0.0.1:4030/healthz
```

Mock-mode startup for adapter-only testing:

```bash
cd /Users/junweili1992163.com/ljwStudy/study-ai/tenx-ai-tts-adapter
source .venv/bin/activate

export TENX_TTS_ADAPTER_API_KEYS=local-dev-key
export TTS_ADAPTER_STORAGE_ROOT=storage/audio
export TTS_ADAPTER_ENABLE_MOCK=true
export COSYVOICE_COMMAND=

uvicorn app.main:app --host 0.0.0.0 --port 4030 --reload
```

## VideoAgent

Point `video-agent` to this adapter:

```bash
export TTS_ADAPTER_BASE_URL=http://127.0.0.1:4030/v1
export TTS_ADAPTER_API_KEY=local-dev-key
export VIDEO_AGENT_ENABLE_TTS_ADAPTER=true
```

On Windows PowerShell:

```powershell
$env:TTS_ADAPTER_BASE_URL = "http://<Mac-Studio-IP>:4030/v1"
$env:TTS_ADAPTER_API_KEY = "local-dev-key"
$env:VIDEO_AGENT_ENABLE_TTS_ADAPTER = "true"
$env:VIDEO_AGENT_SPEECH_MODEL = "cosyvoice"
$env:VIDEO_AGENT_SPEECH_VOICE = "default"
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

Expected result:

```text
voice.wav
```

Temporary adapter output is stored under:

```text
storage/audio/
```

`video-agent` stores its own project copy under:

```text
video-agent/storage/projects/<project_id>/audio/voice.wav
```

## Troubleshooting

If `curl /healthz` fails, check that `uvicorn` is running on `0.0.0.0:4030` and the Mac Studio firewall allows inbound traffic from the Windows machine.

If `/v1/audio/speech` returns `401`, make sure the request uses:

```text
Authorization: Bearer local-dev-key
```

If the response says `COSYVOICE_COMMAND is not configured`, either configure the real CosyVoice command or set:

```bash
export TTS_ADAPTER_ENABLE_MOCK=true
```

If the command exits successfully but no audio is returned, check that your CosyVoice wrapper writes the wav file exactly to the path passed by `{output}`.

## Test

```bash
python -m unittest discover -s tests
```
