from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uuid
import sys

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kokoclone_src'))

router = APIRouter(prefix="/synthesize", tags=["Synthesis"])

VOICE_PROFILES_DIR = "voice_profiles"
AUDIO_OUTPUT_DIR = "audio_output"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

TTS_SECRET_KEY = os.getenv("TTS_SECRET_KEY")

# loading kokoclone once on start up
_cloner = None

def get_cloner():
    global _cloner
    if _cloner is None:
        from core.cloner import KokoClone
        _cloner = KokoClone()
    return _cloner


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
    reference_audio = os.path.join(profile_dir, "sample.wav")

    if not os.path.exists(profile_dir):
        raise HTTPException(
            status_code=404,
            detail="Voice profile not found"
        )

    if not os.path.exists(reference_audio):
        raise HTTPException(
            status_code=404,
            detail="Voice sample not found for this profile"
        )

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    audio_id = str(uuid.uuid4())
    output_path = os.path.join(AUDIO_OUTPUT_DIR, f"{audio_id}.wav")

    try:
        cloner = get_cloner()
        cloner.generate(
            text=request.text,
            lang="en",
            reference_audio=reference_audio,
            output_path=output_path
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio generation failed: {str(e)}"
        )

    return FileResponse(
        output_path,
        media_type="audio/wav",
        filename=f"chunk_{request.chapter_index}_{request.chunk_index}.wav"
    )