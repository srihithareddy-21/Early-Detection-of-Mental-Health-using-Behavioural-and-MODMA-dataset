# NeuroScreen — Multimodal Depression Screening

A research-grade multimodal depression screening system combining acoustic voice biomarkers with structured behavioral questionnaires via late fusion.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
Open `frontend/index.html` in a browser, or serve with any static server:
```bash
npx serve frontend/
```

## API Reference

### POST /predict
| Field | Type | Description |
|-------|------|-------------|
| `audio` | file (.wav) | Speech sample, min 30s recommended |
| `b1` | float 0–1 | Sleep domain score |
| `b2` | float 0–1 | Mood domain score |
| `b3` | float 0–1 | Energy domain score |
| `b4` | float 0–1 | Social domain score |

**Response:**
```json
{
  "audio_score": 0.4231,
  "behavioral_score": 0.3750,
  "fusion_score": 0.4038,
  "risk": "Low Risk",
  "confidence": 0.8124
}
```

### GET /health
Returns `{"status": "ok"}`

## Fusion Formula
fusion_score = 0.6 × audio_score + 0.4 × behavioral_score

## Risk Thresholds
| Fusion Score | Classification |
|---|---|
| < 0.45 | Low Risk |
| 0.45 – 0.64 | Moderate Risk |
| ≥ 0.65 | High Risk |

## Model Files
Drop trained models into `backend/models/`:
- `audio_model.h5` — CNN-BiLSTM weights
- `scaler.pkl` — Feature scaler (StandardScaler)

## Disclaimer
NeuroScreen is a research and educational tool only. It is not FDA-cleared or validated for clinical diagnosis.
