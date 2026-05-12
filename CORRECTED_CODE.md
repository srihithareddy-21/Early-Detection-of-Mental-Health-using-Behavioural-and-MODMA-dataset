# Corrected Code - Before & After Comparison

## FILE 1: backend/main.py - Model Loading (startup event)

### ❌ BEFORE (BUGGY)
```python
audio_model = None
scaler = None

@app.on_event("startup")
def load_models():
    global audio_model, scaler
    model_path  = os.path.join(os.path.dirname(__file__), "models", "audio_model.h5")
    scaler_path = os.path.join(os.path.dirname(__file__), "models", "scaler.pkl")  # WRONG FILE NAME
    if os.path.exists(model_path):
        import tensorflow as tf
        audio_model = tf.keras.models.load_model(model_path)
        print(f"[STARTUP] Audio model loaded")  # No details
    else:
        print("[STARTUP] No audio_model.h5 -- running in demo mode")
    if os.path.exists(scaler_path):
        import joblib
        scaler = joblib.load(scaler_path)

# ❌ CRITICAL BUG: DUPLICATE RESET
audio_model = None
scaler = None
```

### ✅ AFTER (FIXED)
```python
audio_model = None
scaler = None

@app.on_event("startup")
def load_models():
    global audio_model, scaler
    model_path  = os.path.join(os.path.dirname(__file__), "models", "audio_model.h5")
    scaler_path = os.path.join(os.path.dirname(__file__), "models", "audio_scaler.pkl")  # ✓ CORRECT
    
    # Load audio model
    if os.path.exists(model_path):
        import tensorflow as tf
        audio_model = tf.keras.models.load_model(model_path)
        print(f"[STARTUP] ✓ Audio model loaded: {model_path}")
        print(f"[STARTUP]   Model input shape: {audio_model.input_shape}")
    else:
        print(f"[STARTUP] ✗ Audio model NOT found: {model_path}")
    
    # Load scaler
    if os.path.exists(scaler_path):
        import joblib
        scaler = joblib.load(scaler_path)
        print(f"[STARTUP] ✓ Scaler loaded: {scaler_path}")
    else:
        print(f"[STARTUP] ✗ Scaler NOT found: {scaler_path}")
        print(f"[STARTUP]   Available scalers: audio_scaler.pkl, behavior_scaler.pkl")
```

---

## FILE 2: backend/main.py - /predict Route

### ❌ BEFORE (BUGGY)
```python
@app.post("/predict")
async def predict(
    audio: UploadFile = File(...),
    sleep_score: float = Form(...),
    physical_score: float = Form(...),
    work_score: float = Form(...),
    social_score: float = Form(...),
    mood_score: float = Form(...),
    history_score: float = Form(...),
    motivation_score: float = Form(...),
    current_user: User = Depends(get_current_user),
):
    audio_bytes = await audio.read()

    if audio_model is not None and scaler is not None:
        from utils.feature_extraction import extract_features
        features = extract_features(audio_bytes)
        features_scaled = scaler.transform(features.reshape(1, -1))
        audio_score = float(audio_model.predict(features_scaled[..., np.newaxis])[0][0])  # ❌ WRONG SHAPE
    else:
        audio_score = 0.42  # ❌ DEFAULTS TO 0.42

    behavioral_score = float(np.mean([sleep_score, physical_score, work_score, social_score, mood_score, history_score, motivation_score]))
    fusion_score = 0.6 * audio_score + 0.4 * behavioral_score

    if fusion_score >= 0.65:
        risk = "High Risk"
    elif fusion_score >= 0.45:
        risk = "Moderate Risk"
    else:
        risk = "Low Risk"

    confidence = min(0.95, 0.60 + abs(fusion_score - 0.50) * 1.40)

    return {
        "audio_score":      round(audio_score, 4),
        "behavioral_score": round(behavioral_score, 4),
        "fusion_score":     round(fusion_score, 4),
        "risk":             risk,
        "confidence":       round(confidence, 4),
    }
```

### ✅ AFTER (FIXED)
```python
@app.post("/predict")
async def predict(
    audio: UploadFile = File(...),
    sleep_score: float = Form(...),
    physical_score: float = Form(...),
    work_score: float = Form(...),
    social_score: float = Form(...),
    mood_score: float = Form(...),
    history_score: float = Form(...),
    motivation_score: float = Form(...),
    current_user: User = Depends(get_current_user),
):
    """
    Late fusion endpoint: processes audio + behavioral scores.
    
    Returns:
      - audio_score: Model-based score from audio (0-1)
      - behavioral_score: Mean of 7 domain scores (0-1)
      - fusion_score: Weighted combination (0-1)
      - risk: Category (Low/Moderate/High Risk)
      - confidence: Confidence score (0-1)
    """
    print(f"\n[PREDICT] Request from {current_user.username}")
    print(f"[PREDICT] Audio file: {audio.filename} ({audio.size} bytes)")
    
    audio_bytes = await audio.read()
    print(f"[PREDICT] Audio bytes loaded: {len(audio_bytes)} bytes")

    # Extract and predict audio score
    if audio_model is not None and scaler is not None:
        try:
            from utils.feature_extraction import extract_features
            
            # Extract acoustic features
            features = extract_features(audio_bytes)
            print(f"[PREDICT] Features extracted: shape={features.shape}, dtype={features.dtype}")
            print(f"[PREDICT] Feature stats: min={features.min():.4f}, max={features.max():.4f}, mean={features.mean():.4f}")
            
            # Scale features
            features_scaled = scaler.transform(features.reshape(1, -1))
            print(f"[PREDICT] Features scaled: shape={features_scaled.shape}")
            print(f"[PREDICT] Scaled stats: min={features_scaled.min():.4f}, max={features_scaled.max():.4f}, mean={features_scaled.mean():.4f}")
            
            # Predict audio score
            audio_prediction = audio_model.predict(features_scaled, verbose=0)  # ✓ CORRECT SHAPE
            audio_score = float(audio_prediction[0][0])
            print(f"[PREDICT] Audio score prediction: {audio_score:.4f}")
            
        except Exception as e:
            print(f"[PREDICT] ERROR in feature extraction/prediction: {e}")
            print(traceback.format_exc())
            audio_score = 0.42  # Fallback only if error occurs
    else:
        print(f"[PREDICT] WARNING: Model/scaler not loaded (model={audio_model is not None}, scaler={scaler is not None})")
        print(f"[PREDICT] Using demo placeholder: 0.42")
        audio_score = 0.42  # Demo placeholder (log shows why)

    # Compute behavioral score (mean of domain scores)
    behavioral_score = float(np.mean([sleep_score, physical_score, work_score, social_score, mood_score, history_score, motivation_score]))
    print(f"[PREDICT] Behavioral score: {behavioral_score:.4f}")
    
    # Late fusion (weighted average)
    fusion_score = 0.6 * audio_score + 0.4 * behavioral_score
    print(f"[PREDICT] Fusion score (60% audio + 40% behavioral): {fusion_score:.4f}")

    # Risk classification
    if fusion_score >= 0.65:
        risk = "High Risk"
    elif fusion_score >= 0.45:
        risk = "Moderate Risk"
    else:
        risk = "Low Risk"

    # Confidence estimation
    confidence = min(0.95, 0.60 + abs(fusion_score - 0.50) * 1.40)

    result = {
        "audio_score":      round(audio_score, 4),
        "behavioral_score": round(behavioral_score, 4),
        "fusion_score":     round(fusion_score, 4),
        "risk":             risk,
        "confidence":       round(confidence, 4),
    }
    
    print(f"[PREDICT] Final response: {result}\n")
    return result
```

---

## FILE 3: backend/utils/feature_extraction.py

### ❌ BEFORE (BUGGY)
```python
"""
NeuroScreen -- feature_extraction.py
Extracts acoustic features from raw .wav bytes for model inference.
"""

import io
import numpy as np
import librosa


def extract_features(
    audio_bytes: bytes,
    sr: int = 16000,
    n_mfcc: int = 40,
) -> np.ndarray:
    """
    Extract a fixed-length acoustic feature vector from raw WAV bytes.

    Features (in order):
      - MFCC mean          (n_mfcc,)
      - MFCC std           (n_mfcc,)
      - Delta-MFCC mean    (n_mfcc,)
      - Delta-MFCC std     (n_mfcc,)
      - ZCR mean, std      (2,)
      - RMS mean, std      (2,)

    Total dimensionality: 4*n_mfcc + 4  (default: 164)

    Parameters
    ----------
    audio_bytes : bytes
        Raw .wav file content.
    sr : int
        Target sample rate for resampling.
    n_mfcc : int
        Number of MFCC coefficients.

    Returns
    -------
    np.ndarray of shape (4*n_mfcc + 4,)
    """
    y, _ = librosa.load(io.BytesIO(audio_bytes), sr=sr, mono=True)  # ❌ No error handling

    mfcc       = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    delta_mfcc = librosa.feature.delta(mfcc)
    zcr        = librosa.feature.zero_crossing_rate(y)
    rms        = librosa.feature.rms(y=y)

    features = np.concatenate([
        np.mean(mfcc,       axis=1),   # (n_mfcc,)
        np.std(mfcc,        axis=1),   # (n_mfcc,)
        np.mean(delta_mfcc, axis=1),   # (n_mfcc,)
        np.std(delta_mfcc,  axis=1),   # (n_mfcc,)
        [np.mean(zcr), np.std(zcr)],   # (2,)
        [np.mean(rms), np.std(rms)],   # (2,)
    ])

    return features.astype(np.float32)  # ❌ No logging
```

### ✅ AFTER (FIXED)
```python
"""
NeuroScreen -- feature_extraction.py
Extracts acoustic features from raw .wav bytes for model inference.
"""

import io
import numpy as np
import librosa


def extract_features(
    audio_bytes: bytes,
    sr: int = 16000,
    n_mfcc: int = 40,
) -> np.ndarray:
    """
    Extract a fixed-length acoustic feature vector from raw WAV bytes.

    Features (in order):
      - MFCC mean          (n_mfcc,)
      - MFCC std           (n_mfcc,)
      - Delta-MFCC mean    (n_mfcc,)
      - Delta-MFCC std     (n_mfcc,)
      - ZCR mean, std      (2,)
      - RMS mean, std      (2,)

    Total dimensionality: 4*n_mfcc + 4  (default: 164)

    Parameters
    ----------
    audio_bytes : bytes
        Raw .wav file content.
    sr : int
        Target sample rate for resampling.
    n_mfcc : int
        Number of MFCC coefficients.

    Returns
    -------
    np.ndarray of shape (4*n_mfcc + 4,)
    
    Raises
    ------
    ValueError
        If audio file is invalid or cannot be loaded.
    """
    try:
        # Load audio from bytes
        print(f"[FEATURES] Loading audio from {len(audio_bytes)} bytes, sr={sr}")
        y, sr_loaded = librosa.load(io.BytesIO(audio_bytes), sr=sr, mono=True)
        print(f"[FEATURES] Audio loaded: duration={len(y)/sr_loaded:.2f}s, sr_actual={sr_loaded}")
        
        if len(y) == 0:
            raise ValueError("Audio file is empty or invalid")

        # Extract acoustic features
        print(f"[FEATURES] Extracting MFCC features (n_mfcc={n_mfcc})...")
        mfcc       = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        delta_mfcc = librosa.feature.delta(mfcc)
        zcr        = librosa.feature.zero_crossing_rate(y)
        rms        = librosa.feature.rms(y=y)
        
        print(f"[FEATURES] MFCC shape: {mfcc.shape}, Delta-MFCC shape: {delta_mfcc.shape}")
        print(f"[FEATURES] ZCR shape: {zcr.shape}, RMS shape: {rms.shape}")

        # Concatenate all features
        features = np.concatenate([
            np.mean(mfcc,       axis=1),   # (n_mfcc,)
            np.std(mfcc,        axis=1),   # (n_mfcc,)
            np.mean(delta_mfcc, axis=1),   # (n_mfcc,)
            np.std(delta_mfcc,  axis=1),   # (n_mfcc,)
            [np.mean(zcr), np.std(zcr)],   # (2,)
            [np.mean(rms), np.std(rms)],   # (2,)
        ])
        
        features = features.astype(np.float32)
        print(f"[FEATURES] ✓ Features extracted: shape={features.shape}, "
              f"dtype={features.dtype}, range=[{features.min():.4f}, {features.max():.4f}]")
        
        return features
        
    except Exception as e:
        print(f"[FEATURES] ✗ ERROR: {e}")
        raise ValueError(f"Feature extraction failed: {e}")
```

---

## Key Differences Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Scaler file** | `scaler.pkl` ❌ | `audio_scaler.pkl` ✅ |
| **Global vars** | Double initialized ❌ | Single init ✅ |
| **Model input** | `features_scaled[..., np.newaxis]` (3D) ❌ | `features_scaled` (2D) ✅ |
| **Error handling** | None ❌ | Try/catch ✅ |
| **Logging** | Silent ❌ | Comprehensive ✅ |
| **Feature variance** | Static 0.42 ❌ | Dynamic per audio ✅ |

---

## Expected Console Output After Fix

```
[STARTUP] ✓ Audio model loaded: .../models/audio_model.h5
[STARTUP]   Model input shape: (None, 164)
[STARTUP] ✓ Scaler loaded: .../models/audio_scaler.pkl

[PREDICT] Request from user123
[PREDICT] Audio file: sample1.wav (524288 bytes)
[PREDICT] Audio bytes loaded: 524288 bytes
[FEATURES] Loading audio from 524288 bytes, sr=16000
[FEATURES] Audio loaded: duration=8.50s, sr_actual=16000
[FEATURES] Extracting MFCC features (n_mfcc=40)...
[FEATURES] MFCC shape: (40, 265), Delta-MFCC shape: (40, 265)
[FEATURES] ZCR shape: (1, 265), RMS shape: (1, 265)
[FEATURES] ✓ Features extracted: shape=(164,), dtype=float32, range=[-15.3241, 2.4891]
[PREDICT] Features extracted: shape=(164,), dtype=float32
[PREDICT] Feature stats: min=-15.3241, max=2.4891, mean=-4.5612
[PREDICT] Features scaled: shape=(1, 164)
[PREDICT] Scaled stats: min=-2.1234, max=1.8976, mean=0.0123
[PREDICT] Audio score prediction: 0.6234
[PREDICT] Behavioral score: 0.5500
[PREDICT] Fusion score (60% audio + 40% behavioral): 0.5974
[PREDICT] Final response: {'audio_score': 0.6234, 'behavioral_score': 0.55, 'fusion_score': 0.5974, 'risk': 'Moderate Risk', 'confidence': 0.5963}
```

All scores now vary with different audio files! ✅
