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
    """
    try:
        print(f"[FEATURES] Loading audio from {len(audio_bytes)} bytes, sr={sr}")
        y, sr_loaded = librosa.load(io.BytesIO(audio_bytes), sr=sr, mono=True)
        print(f"[FEATURES] Audio loaded: duration={len(y)/sr_loaded:.2f}s, sr_actual={sr_loaded}")
        
        if len(y) == 0:
            raise ValueError("Audio file is empty or invalid")

        print(f"[FEATURES] Extracting MFCC features (n_mfcc={n_mfcc})...")
        mfcc       = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        delta_mfcc = librosa.feature.delta(mfcc)
        zcr        = librosa.feature.zero_crossing_rate(y)
        rms        = librosa.feature.rms(y=y)
        
        print(f"[FEATURES] MFCC shape: {mfcc.shape}, Delta-MFCC shape: {delta_mfcc.shape}")
        print(f"[FEATURES] ZCR shape: {zcr.shape}, RMS shape: {rms.shape}")

        features = np.concatenate([
            np.mean(mfcc,       axis=1),
            np.std(mfcc,        axis=1),
            np.mean(delta_mfcc, axis=1),
            np.std(delta_mfcc,  axis=1),
            [np.mean(zcr), np.std(zcr)],
            [np.mean(rms), np.std(rms)],
        ])
        
        features = features.astype(np.float32)
        print(f"[FEATURES] Features extracted: shape={features.shape}, "
              f"dtype={features.dtype}, range=[{features.min():.4f}, {features.max():.4f}]")
        
        return features
        
    except Exception as e:
        print(f"[FEATURES] ERROR: {e}")
        raise ValueError(f"Feature extraction failed: {e}")
