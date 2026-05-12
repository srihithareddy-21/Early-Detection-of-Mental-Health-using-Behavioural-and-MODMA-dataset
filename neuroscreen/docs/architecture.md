# NeuroScreen — System Architecture

## Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    NeuroScreen Frontend                 │
│  Tab 1: Overview  │  Tab 2: Questionnaire               │
│  Tab 3: Fusion    │  Tab 4: Charts                      │
│  Tab 5: About     │                                     │
└───────────────────────────┬─────────────────────────────┘
                            │ POST /predict (multipart)
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │ Audio Branch │    │  Beh Branch  │                   │
│  │              │    │              │                   │
│  │ Librosa      │    │  b1,b2,b3,b4 │                   │
│  │ feature_ext  │    │  → mean()    │                   │
│  │     ↓        │    │      ↓       │                   │
│  │ CNN-BiLSTM   │    │  beh_score   │                   │
│  │     ↓        │    │              │                   │
│  │ audio_score  │    │              │                   │
│  └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                           │
│         └──────────┬────────┘                           │
│                    ▼                                    │
│         fusion = 0.6*audio + 0.4*beh                    │
│         risk classification + confidence                │
└─────────────────────────────────────────────────────────┘
```

## Data Flow
1. User uploads .wav file + submits questionnaire
2. Frontend sends multipart POST to `/predict`
3. Backend extracts 164-dim feature vector via librosa
4. CNN-BiLSTM maps features → sigmoid probability
5. Behavioural score computed as mean of 4 domain scores
6. Late fusion: `fusion = 0.6 × audio + 0.4 × behavioral`
7. Risk classified by thresholds (0.45 / 0.65)
8. Results returned as JSON → rendered in UI

## Fusion Formula
```
fusion_score = α × audio_score + β × behavioral_score
             = 0.6 × audio_score + 0.4 × behavioral_score
```

Confidence: `min(0.95, 0.60 + |fusion − 0.50| × 1.40)`
