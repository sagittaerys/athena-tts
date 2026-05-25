from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/synthesize", tags=["Synthesis"])

VOICE_PROFILES_DIR = "voice_profiles"
AUDIO_OUTPUT_DIR = "audio_output"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

TTS_SECRET_KEY = os.getenv("TTS_SECRET_KEY")


def verify_secret(x_secret_key: str = Header(None)):
    if x_secret_key != TTS_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


class SynthesisRequest(BaseModel):
    voice_profile_id: str
    text: str
    chunk_index: int = 0
    chapter_index: int = 0


@router.post("/")
async def synthesize(
    request: SynthesisRequest,
    x_secret_key: str = Header(None)
):
    verify_secret(x_secret_key)

    profile_dir = os.path.join(VOICE_PROFILES_DIR, request.voice_profile_id)
    if not os.path.exists(profile_dir):
        raise HTTPException(
            status_code=404,
            detail="Voice profile not found"
        )

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    audio_id = str(uuid.uuid4())
    output_path = os.path.join(AUDIO_OUTPUT_DIR, f"{audio_id}.wav")

    generate_audio(
        text=request.text,
        voice_profile_dir=profile_dir,
        output_path=output_path
    )

    return FileResponse(
        output_path,
        media_type="audio/wav",
        filename=f"chunk_{request.chapter_index}_{request.chunk_index}.wav"
    )


def generate_audio(text: str, voice_profile_dir: str, output_path: str):
    # i'm generating a silent wav for now --- awaiting kokoro integration
    import wave
    import struct

    sample_rate = 22050
    duration = 1
    num_samples = sample_rate * duration

    with wave.open(output_path, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        data = struct.pack("<" + "h" * num_samples, *([0] * num_samples))
        wav_file.writeframes(data)