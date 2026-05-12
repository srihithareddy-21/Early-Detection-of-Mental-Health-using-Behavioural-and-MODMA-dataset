"""
NeuroScreen -- generate_demo_models.py
Creates demo models with synthetic data to make the app fully functional.
Uses scikit-learn RandomForest for compatibility with Python 3.14+
"""

import os
import sys
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

print("[SETUP] Generating demo models for NeuroScreen...")

# === 1. Create synthetic training data ===
print("\n[SETUP] Creating synthetic dataset...")
np.random.seed(42)

# Synthetic features: 164 acoustic features (40 mfcc + 40 mfcc_std + 40 delta + 40 delta_std + 2 zcr + 2 rms)
n_samples = 500
n_features = 164

# Class 0: Healthy (lower energy features)
X_class0 = np.random.normal(loc=-0.2, scale=0.8, size=(n_samples // 2, n_features))
y_class0 = np.zeros(n_samples // 2)

# Class 1: Depression (higher variance in features)
X_class1 = np.random.normal(loc=0.3, scale=1.2, size=(n_samples // 2, n_features))
y_class1 = np.ones(n_samples // 2)

X = np.vstack([X_class0, X_class1]).astype(np.float32)
y = np.hstack([y_class0, y_class1]).astype(np.float32)

# Shuffle
shuffle_idx = np.random.permutation(len(X))
X = X[shuffle_idx]
y = y[shuffle_idx]

print(f"  ✓ Dataset shape: {X.shape}")
print(f"  ✓ Labels: {int(y.sum())} positive, {len(y) - int(y.sum())} negative")
print(f"  ✓ Class balance: {100 * y.mean():.1f}% positive")

# === 2. Create and fit scaler ===
print("\n[SETUP] Training feature scaler...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"  ✓ Scaler fitted on {X_scaled.shape[0]} samples")
print(f"  ✓ Feature means (first 5): {scaler.mean_[:5]}")
print(f"  ✓ Feature stds (first 5): {scaler.scale_[:5]}")

# === 3. Build RandomForest model (scikit-learn) ===
print("\n[SETUP] Building RandomForest model...")

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced',
)

print(f"  ✓ Model initialized: RandomForestClassifier")

# === 4. Train model ===
print("\n[SETUP] Training model on synthetic data...")

model.fit(X_scaled, y)

# Evaluate
train_acc = model.score(X_scaled, y)
train_proba = model.predict_proba(X_scaled)[:, 1]

print(f"  ✓ Training complete")
print(f"  ✓ Final train accuracy: {train_acc:.4f}")
print(f"  ✓ Probability range: [{train_proba.min():.4f}, {train_proba.max():.4f}]")
print(f"  ✓ Mean probability: {train_proba.mean():.4f}")

# === 5. Save model and scaler ===
print("\n[SETUP] Saving artifacts...")
model_dir = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(model_dir, exist_ok=True)

# Save as pickle with .h5 extension for compatibility with backend code
model_path = os.path.join(model_dir, "audio_model.h5")
scaler_path = os.path.join(model_dir, "audio_scaler.pkl")

joblib.dump(model, model_path)
print(f"  ✓ Model saved: {model_path}")

joblib.dump(scaler, scaler_path)
print(f"  ✓ Scaler saved: {scaler_path}")

# === 6. Verify ===
print("\n[SETUP] Verifying saved artifacts...")
test_features = X_scaled[:5]
predictions = model.predict_proba(test_features)[:, 1]
print(f"  ✓ Model predictions on first 5 samples: {predictions}")

loaded_scaler = joblib.load(scaler_path)
test_scaled = loaded_scaler.transform(test_features)
print(f"  ✓ Scaler works: scaled mean={test_scaled.mean():.4f}, std={test_scaled.std():.4f}")

loaded_model = joblib.load(model_path)
test_proba = loaded_model.predict_proba(test_scaled)[:, 1]
print(f"  ✓ Loaded model predictions: {test_proba}")

print("\n" + "="*60)
print("[SETUP] ✓ Demo models generated successfully!")
print("="*60)
print(f"Ready to start backend with:")
print(f"  cd neuroscreen/backend")
print(f"  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
