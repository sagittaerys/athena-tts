import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import io

os.environ["TTS_SECRET_KEY"] = "test_secret"

from main import app

client = TestClient(app)
SECRET = "test_secret"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_unauthorized_without_key():
    response = client.post("/clone/")
    assert response.status_code == 422


def test_clone_unauthorized():
    audio = io.BytesIO(b"fake audio data")
    response = client.post(
        "/clone/",
        headers={"x-secret-key": "wrong_key"},
        files={"file": ("test.wav", audio, "audio/wav")}
    )
    assert response.status_code == 401


def test_clone_rejects_non_audio():
    fake_file = io.BytesIO(b"not audio")
    response = client.post(
        "/clone/",
        headers={"x-secret-key": SECRET},
        files={"file": ("test.txt", fake_file, "text/plain")}
    )
    assert response.status_code == 400


def test_clone_success():
    audio = io.BytesIO(b"fake audio data")
    response = client.post(
        "/clone/",
        headers={"x-secret-key": SECRET},
        files={"file": ("test.wav", audio, "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "voice_profile_id" in data
    assert data["status"] == "ready"


def test_synthesize_unauthorized():
    response = client.post(
        "/synthesize/",
        headers={"x-secret-key": "wrong_key"},
        json={
            "voice_profile_id": "fake-id",
            "text": "Hello world",
            "chunk_index": 0,
            "chapter_index": 0
        }
    )
    assert response.status_code == 401


def test_synthesize_missing_profile():
    response = client.post(
        "/synthesize/",
        headers={"x-secret-key": SECRET},
        json={
            "voice_profile_id": "nonexistent-id",
            "text": "Hello world",
            "chunk_index": 0,
            "chapter_index": 0
        }
    )
    assert response.status_code == 404


def test_synthesize_empty_text():
    os.makedirs("voice_profiles/test-profile", exist_ok=True)
    response = client.post(
        "/synthesize/",
        headers={"x-secret-key": SECRET},
        json={
            "voice_profile_id": "test-profile",
            "text": "",
            "chunk_index": 0,
            "chapter_index": 0
        }
    )
    assert response.status_code == 400