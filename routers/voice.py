from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from pydantic import BaseModel
import os
import uuid
import shutil
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/clone", tags=["Voice"])

VOICE_PROFILES_DIR = "voice_profiles"
os.makedirs(VOICE_PROFILES_DIR, exist_ok=True)

TTS_SECRET_KEY = os.getenv("TTS_SECRET_KEY")


def verify_secret(x_secret_key: str = Header(None)):
    print(f"Received key: '{x_secret_key}'")
    print(f"Expected key: '{TTS_SECRET_KEY}'")
    if x_secret_key != TTS_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/")
async def clone_voice(
    file: UploadFile = File(...),
    x_secret_key: str = Header(None)
):
    verify_secret(x_secret_key)

    if not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an audio file"
        )

    voice_profile_id = str(uuid.uuid4())
    profile_dir = os.path.join(VOICE_PROFILES_DIR, voice_profile_id)
    os.makedirs(profile_dir, exist_ok=True)

    file_path = os.path.join(profile_dir, "sample.wav")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "voice_profile_id": voice_profile_id,
        "status": "ready",
        "message": "Voice profile created successfully"
    }