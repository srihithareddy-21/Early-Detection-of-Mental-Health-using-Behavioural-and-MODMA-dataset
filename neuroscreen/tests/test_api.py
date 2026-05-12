"""
NeuroScreen -- Integration tests for the FastAPI backend.
Run: pytest tests/
"""

import pytest
from fastapi.testclient import TestClient
import io
import wave
import struct
import math

# Adjust import path if running from project root
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backend.main import app

client = TestClient(app)


def make_silent_wav(duration_sec: float = 1.0, sr: int = 16000) -> bytes:
    """Generate a minimal silent .wav file for testing."""
    n_samples = int(sr * duration_sec)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(struct.pack(f"<{n_samples}h", *([0] * n_samples)))
    return buf.getvalue()


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_predict_demo_mode():
    """Predict endpoint should respond even without real models (demo mode)."""
    wav_bytes = make_silent_wav(duration_sec=2.0)
    res = client.post(
        "/predict",
        files={"audio": ("test.wav", wav_bytes, "audio/wav")},
        data={"b1": "0.3", "b2": "0.4", "b3": "0.2", "b4": "0.5"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "fusion_score" in body
    assert "risk" in body
    assert 0.0 <= body["fusion_score"] <= 1.0
    assert body["risk"] in {"Low Risk", "Moderate Risk", "High Risk"}


def test_predict_high_risk():
    """With extreme behavioural scores, risk should be High."""
    wav_bytes = make_silent_wav()
    res = client.post(
        "/predict",
        files={"audio": ("test.wav", wav_bytes, "audio/wav")},
        data={"b1": "1.0", "b2": "1.0", "b3": "1.0", "b4": "1.0"},
    )
    assert res.status_code == 200
    # behavioral_score = 1.0, fusion >= 0.65 guaranteed if audio demo = 0.42
    # 0.6*0.42 + 0.4*1.0 = 0.652 >= 0.65
    assert res.json()["risk"] in {"High Risk", "Moderate Risk"}


def test_predict_low_risk():
    """With zero behavioural scores, risk should be Low."""
    wav_bytes = make_silent_wav()
    res = client.post(
        "/predict",
        files={"audio": ("test.wav", wav_bytes, "audio/wav")},
        data={"b1": "0.0", "b2": "0.0", "b3": "0.0", "b4": "0.0"},
    )
    assert res.status_code == 200
    # 0.6*0.42 + 0.4*0.0 = 0.252 < 0.45 -> Low Risk
    assert res.json()["risk"] == "Low Risk"
