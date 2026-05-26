# athena-tts

> Voice cloning and synthesis server for Athena.

This is the Python FastAPI service that handles voice cloning and text-to-speech synthesis for Athena. It accepts a short audio recording of a user's voice, creates a voice profile, and synthesizes any text in that voice as audio.

This service is **internal** — it only accepts requests from the Rails API (`athena-api`). It is never exposed directly to the mobile app.

---

## Related repositories

| Repository | Description |
|---|---|
| [athena-api](https://github.com/sagittaerys/athena-api) | Rails 8 backend |
| [athena-mobile](https://github.com/sagittaerys/athena-mobile) | React Native mobile app |
| [athena-tts](https://github.com/sagittaerys/athena-tts) | This repo — TTS server |

---

## Endpoints

All endpoints require the `x-secret-key` header matching `TTS_SECRET_KEY` in `.env`.

GET  /health        — health check
POST /clone/        — upload voice sample, receive voice_profile_id
POST /synthesize/   — synthesize text in a cloned voice, receive WAV audio

---

## Local setup

```bash
# Clone the repo
git clone https://github.com/sagittaerys/athena-tts
cd athena-tts

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in your TTS_SECRET_KEY

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Docker setup

```bash
cp .env.example .env
# Fill in your TTS_SECRET_KEY

docker-compose up --build
```

---

## Environment variables

```bash
TTS_SECRET_KEY=your_secret_key  # shared secret with athena-api
HOST=0.0.0.0
PORT=8000
```

---

## Running tests

```bash
source venv/bin/activate
pytest test_main.py -v
```

---

## License

MIT