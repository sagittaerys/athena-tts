from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from routers import voice, synthesis

load_dotenv()

app = FastAPI(
    title="Athena TTS Server",
    description="Voice cloning and synthesis server for Athena",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(voice.router)
app.include_router(synthesis.router)

TTS_SECRET_KEY =os.getenv("TTS_SECRET_KEY")

def verify_secret(x_secret_key: str = None):
    if x_secret_key != TTS_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "athena-tts"}


@app.get("/")
def root():
    return {"message": "Athena TTS Server is running"}