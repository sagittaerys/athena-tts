# athena-tts

> Voice cloning and synthesis server for Athena.

This is the Python FastAPI service that handles voice cloning and text-to-speech synthesis for Athena. It accepts a short audio recording of a user's voice, creates a voice profile, and synthesizes any text in that voice(reference) as audio.

This service is **internal** as it only accepts requests from the Rails API (`athena-api`). It is never exposed directly to the mobile app.

---

## How it works

Voice synthesis in Athena is a two-phase process:

```
Phase 1 — Kokoro TTS
  Text → Kokoro-82M → natural speech in a preset voice

Phase 2 — Kanade Voice Conversion
  Preset voice audio + your voice sample → Kanade → audio in YOUR voice
```

Kokoro handles natural speech synthesis. Kanade transfers your voice characteristics onto that speech. The result is text read aloud in a voice that sounds like you.

---

## Related repositories

| Repository | Description |
|---|---|
| [athena-api](https://github.com/sagittaerys/athena-api) | Rails 8 backend |
| [athena-mobile](https://github.com/sagittaerys/athena-mobile) | React Native mobile app (WIP) |

---

## Tech stack

- **Python 3.12**
- **FastAPI** — API framework
- **uvicorn** — ASGI server
- **Kokoro-82M** — open weight TTS model (Apache 2.0)
- **KokoClone** — voice cloning layer built on Kokoro-ONNX
- **Kanade** — speech tokenizer for voice conversion
- **PyTorch** (CPU) — ML inference engine

---

## Endpoints

All endpoints require the `x-secret-key` header matching `TTS_SECRET_KEY` in `.env`.

```
GET  /health        — health check
POST /clone/        — upload voice sample (WAV), receive voice_profile_id
POST /synthesize/   — synthesize text in a cloned voice, receive WAV audio
```

---

## Prerequisites

- Python 3.12+
- espeak-ng (system dependency)
- ~2GB RAM minimum
- ~2GB disk space for model weights (downloaded automatically on first run)

---

## Local setup

```bash
# Clone the repo
git clone https://github.com/sagittaerys/athena-tts
cd athena-tts

# install system dependency
sudo apt-get install espeak-ng -y

# create and activate virtual environment (venv)
python3 -m venv venv
source venv/bin/activate

# install PyTorch CPU version first (must be installed before other deps)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
pip install -r requirements.txt

# clone KokoClone (voice cloning engine)
git clone https://github.com/Ashish-Patnaik/kokoclone.git kokoclone_src

# set up environment variables
cp .env.example .env
# fill in your TTS_SECRET_KEY and HF_TOKEN

# start your server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** On first run the server automatically downloads model weights (~1.5GB total) from HuggingFace. This is a one-time download. Set `HF_TOKEN` in `.env` for faster, rate-limit-free downloads.

---

## Docker setup

```bash
cp .env.example .env
# Fill in your TTS_SECRET_KEY and HF_TOKEN

docker-compose up --build
```

---

## Environment variables

Copy `.env.example` to `.env` and fill in:

```bash
TTS_SECRET_KEY=your_shared_secret_with_athena_api
HF_TOKEN=your_huggingface_read_token
HOST=0.0.0.0
PORT=8000
```

you'll have generate a strong secret key with:

```bash
openssl rand -hex 32
```

Use the same value for `TTS_SECRET_KEY` in both `athena-api` and `athena-tts` for uniformity.

Get a free HuggingFace token at: https://huggingface.co/settings/tokens (Read access only)

---

## Running tests

```bash
source venv/bin/activate
pytest test_main.py -v
```

---

## Model weights

Model weights are downloaded automatically on first run from HuggingFace:

```
Kokoro-82M ONNX     ~92MB   (speech synthesis)
voices-v1.0.bin     ~28MB   (voice style vectors)
Kanade-12.5hz       ~480MB  (voice conversion)
WavLM               ~360MB  (voice feature extraction)
Vocos vocoder       ~55MB   (audio reconstruction)
─────────────────────────────
Total               ~1.0GB
```

Weights are cached in `~/.cache/huggingface/` after the first download.

---

## Acknowledgements

Voice cloning powered by [KokoClone](https://github.com/Ashish-Patnaik/kokoclone) by Ashish Patnaik, built on [Kokoro-82M](https://github.com/hexgrad/kokoro) by hexgrad. Speech tokenization via [Kanade](https://github.com/frothywater/kanade-tokenizer) by frothywater. All licensed under Apache 2.0.

---

## Contributing

1. Fork the repository
2. Create a feature branch — `git checkout -b feat/your-feature`
3. Write tests for your changes
4. Ensure all tests pass — `pytest test_main.py -v`
5. Submit a pull request

---

## License

Apache 2.0