"""
NeuroScreen -- train.py
CNN-BiLSTM training script template.

Usage:
    python -m backend.utils.train \
        --features data/processed/features.npy \
        --labels   data/processed/labels.npy \
        --out      backend/models/
"""

import argparse
import os
import numpy as np
import joblib
import tensorflow as tf
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score


def build_model(input_dim: int) -> tf.keras.Model:
    """CNN-BiLSTM for acoustic depression detection."""
    inputs = tf.keras.Input(shape=(input_dim, 1), name="features")

    # Convolutional feature extraction
    x = tf.keras.layers.Conv1D(64, kernel_size=3, activation="relu", padding="same")(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv1D(128, kernel_size=3, activation="relu", padding="same")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling1D(pool_size=2)(x)
    x = tf.keras.layers.Dropout(0.25)(x)

    # Temporal modelling
    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=False))(x)
    x = tf.keras.layers.Dropout(0.30)(x)

    # Classification head
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid", name="probability")(x)

    return tf.keras.Model(inputs, outputs, name="NeuroScreen_CNN_BiLSTM")


def train(features_path: str, labels_path: str, out_dir: str, n_splits: int = 5):
    X = np.load(features_path)   # (n_samples, n_features)
    y = np.load(labels_path)     # (n_samples,) binary

    print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, "
          f"{int(y.sum())} positive ({100*y.mean():.1f}%)")

    os.makedirs(out_dir, exist_ok=True)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_aucs = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        print(f"\n{'='*50}\nFold {fold + 1}/{n_splits}")

        # Scale features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X[train_idx])
        X_val   = scaler.transform(X[val_idx])

        # Reshape for Conv1D: (batch, timesteps, channels)
        X_train_3d = X_train[..., np.newaxis]
        X_val_3d   = X_val[..., np.newaxis]

        # Build and compile model
        model = build_model(X.shape[1])
        model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-3),
            loss="binary_crossentropy",
            metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
        )

        # Class weights for imbalance
        n_neg, n_pos = int((1 - y[train_idx]).sum()), int(y[train_idx].sum())
        class_weight = {0: 1.0, 1: n_neg / max(n_pos, 1)}

        callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True, monitor="val_auc", mode="max"),
            tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=4, monitor="val_loss"),
        ]

        model.fit(
            X_train_3d, y[train_idx],
            validation_data=(X_val_3d, y[val_idx]),
            epochs=100,
            batch_size=32,
            class_weight=class_weight,
            callbacks=callbacks,
            verbose=1,
        )

        val_probs = model.predict(X_val_3d, verbose=0).ravel()
        auc = roc_auc_score(y[val_idx], val_probs)
        fold_aucs.append(auc)
        print(f"Fold {fold+1} AUC: {auc:.4f}")

        # Save best fold
        if auc == max(fold_aucs):
            model.save(os.path.join(out_dir, "audio_model.h5"))
            joblib.dump(scaler, os.path.join(out_dir, "scaler.pkl"))
            print(f"  -> Saved best model (fold {fold+1})")

    print(f"\nCV AUC: {np.mean(fold_aucs):.4f} ± {np.std(fold_aucs):.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", default="data/processed/features.npy")
    parser.add_argument("--labels",   default="data/processed/labels.npy")
    parser.add_argument("--out",      default="backend/models/")
    parser.add_argument("--folds",    type=int, default=5)
    args = parser.parse_args()
    train(args.features, args.labels, args.out, args.folds)
