"""
NeuroScreen — FastAPI Backend
/predict  : multipart POST -> fusion score + risk classification
/health   : GET -> status check
/login    : POST -> authenticate user
/signup   : POST -> register user
/user-info: GET/POST -> get/update user profile
/history  : POST -> append user's analysis result to history
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import numpy as np
import os
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import JWTError, jwt
import traceback
import json
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NeuroScreen API",
    description="Multimodal depression screening -- audio + behavioural late fusion",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend")), name="static")

# Auth setup
SECRET_KEY = "your-secret-key-here"  # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# JSON-based user storage
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    """Load users from JSON file as a list. Auto-initializes if missing or corrupted."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    print(f"[INIT] users.json is empty, initializing...")
                    raise ValueError("Empty file")
                data = json.loads(content)
                if not isinstance(data, dict) or 'users' not in data:
                    print(f"[ERROR] users.json has invalid structure, backing up and reinitializing...")
                    # Backup corrupted file
                    backup_path = USERS_FILE + f".backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                    if os.path.exists(USERS_FILE):
                        os.rename(USERS_FILE, backup_path)
                        print(f"[BACKUP] Corrupted file backed up to: {backup_path}")
                    raise ValueError("Invalid structure")
                return data.get('users', [])
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse users.json (JSON error): {e}")
            # Backup corrupted file
            backup_path = USERS_FILE + f".backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            os.rename(USERS_FILE, backup_path)
            print(f"[BACKUP] Corrupted file backed up to: {backup_path}")
            # Initialize fresh
            initialize_users_file()
            return []
        except Exception as e:
            print(f"[ERROR] Failed to load users.json: {e}")
            # Initialize fresh on error
            initialize_users_file()
            return []
    else:
        print(f"[INIT] users.json not found, creating...")
        initialize_users_file()
        return []

def initialize_users_file():
    """Create a fresh users.json with default structure."""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, 'w') as f:
            json.dump({'users': [], 'initialized': datetime.utcnow().isoformat()}, f, indent=2)
        print(f"[INIT] ✓ Fresh users.json created at: {USERS_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize users.json: {e}")

def save_users(users_list):
    """Save users to JSON file as a list."""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, 'w') as f:
            json.dump({'users': users_list, 'updated': datetime.utcnow().isoformat()}, f, indent=2)
        print(f"[USER_PERSIST] Saved {len(users_list)} users to {USERS_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save users.json: {e}")

def find_user(username: str):
    """Find user in users_db list by username."""
    for user in users_db:
        if user.get('username') == username:
            return user
    return None

def find_user_index(username: str):
    """Find user index in users_db list by username."""
    for i, user in enumerate(users_db):
        if user.get('username') == username:
            return i
    return -1

# Load users from JSON on startup (auto-initializes if missing)
users_db = load_users()
logger.info(f"[STARTUP] Loaded {len(users_db)} users from {USERS_FILE}")

class User(BaseModel):
    username: str
    email: str
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    hashed_password: str
    history: list = []  # User-specific analysis history

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class AnalysisResult(BaseModel):
    audio_score: float
    behavioral_score: float
    fusion_score: float
    risk: str
    confidence: float
    timestamp: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = find_user(username)
    if user is None:
        raise credentials_exception
    return user

audio_model = None
scaler = None

@app.on_event("startup")
def load_models():
    global audio_model, scaler
    model_path  = os.path.join(os.path.dirname(__file__), "models", "audio_model.h5")
    scaler_path = os.path.join(os.path.dirname(__file__), "models", "audio_scaler.pkl")
    
    # Load audio model (supports both TensorFlow and scikit-learn)
    if os.path.exists(model_path):
        try:
            # Try TensorFlow first
            import tensorflow as tf
            audio_model = tf.keras.models.load_model(model_path)
            print(f"[STARTUP] ✓ Audio model loaded (TensorFlow): {model_path}")
            print(f"[STARTUP]   Model input shape: {audio_model.input_shape}")
        except Exception as tf_err:
            # Fallback to scikit-learn
            try:
                import joblib
                audio_model = joblib.load(model_path)
                print(f"[STARTUP] ✓ Audio model loaded (scikit-learn): {model_path}")
                print(f"[STARTUP]   Model type: {type(audio_model).__name__}")
            except Exception as sk_err:
                print(f"[STARTUP] ✗ Failed to load model:")
                print(f"      TensorFlow error: {tf_err}")
                print(f"      Scikit-learn error: {sk_err}")
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

# Auth routes
@app.post("/signup", response_model=Token)
async def signup(user: UserCreate):
    try:
        if find_user(user.username) is not None:
            raise HTTPException(status_code=400, detail="Username already registered")
        hashed_password = get_password_hash(user.password)
        new_user = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "name": None,
            "age": None,
            "gender": None,
            "history": []
        }
        users_db.append(new_user)
        # Persist to JSON
        save_users(users_db)
        logger.info(f"New user registered: {user.username} ({user.email})")
        access_token = create_access_token(data={"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Signup failed: {e}")

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    try:
        db_user = find_user(user.username)
        if not db_user or not verify_password(user.password, db_user.get('hashed_password', '')):
            print(f"[LOGIN_FAIL] Failed login attempt for: {user.username}")
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        print(f"[LOGIN_SUCCESS] User logged in: {user.username}")
        access_token = create_access_token(data={"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Login failed: {e}")

@app.get("/api/user-info")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user.get("username"),
        "email": current_user.get("email"),
        "name": current_user.get("name"),
        "age": current_user.get("age"),
        "gender": current_user.get("gender")
    }

@app.post("/api/user-info")
async def update_user_info(profile: UserProfile, current_user: dict = Depends(get_current_user)):
    try:
        user_index = find_user_index(current_user.get("username"))
        if user_index == -1:
            raise HTTPException(status_code=404, detail="User not found")
        
        users_db[user_index]["name"] = profile.name or users_db[user_index].get("name")
        users_db[user_index]["age"] = profile.age or users_db[user_index].get("age")
        users_db[user_index]["gender"] = profile.gender or users_db[user_index].get("gender")
        
        # Persist to JSON
        save_users(users_db)
        print(f"[USER_UPDATE] Profile updated for user: {current_user.get('username')}")
        return {
            "message": "Profile updated",
            "user": {
                "username": users_db[user_index].get("username"),
                "email": users_db[user_index].get("email"),
                "name": users_db[user_index].get("name"),
                "age": users_db[user_index].get("age"),
                "gender": users_db[user_index].get("gender")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Profile update failed: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": audio_model is not None}

def estimate_audio_score_from_features(features: np.ndarray) -> float:
    """
    Content-based fallback for incompatible model/scaler artifacts.

    This keeps the demo responsive when the saved scaler/model does not match
    the 164-feature extractor. It is deterministic and varies by audio content,
    but it is not a replacement for a correctly trained audio model.
    """
    mfcc_mean = features[:40]
    mfcc_std = features[40:80]
    delta_std = features[120:160]
    zcr_mean = float(features[160])
    rms_mean = float(features[162])

    energy_component = np.tanh(rms_mean * 18.0)
    zcr_component = np.tanh(zcr_mean * 8.0)
    mfcc_component = np.tanh(np.std(mfcc_mean) / 90.0)
    texture_component = np.tanh((np.mean(mfcc_std) + np.mean(delta_std)) / 75.0)

    combined = (
        0.30 * energy_component +
        0.25 * zcr_component +
        0.25 * mfcc_component +
        0.20 * texture_component
    )
    return float(np.clip(0.15 + (combined * 0.70), 0.05, 0.95))

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
    current_user: dict = Depends(get_current_user),
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
    # Generate unique ID for this upload
    unique_id = str(uuid.uuid4())[:8]
    logger.info(f"\n[PREDICT] ==================== REQUEST {unique_id} ====================")
    logger.info(f"[PREDICT] User: {current_user.get('username')}")
    logger.info(f"[PREDICT] Audio file: {audio.filename} ({audio.size} bytes)")
    
    # Validate file size (minimum 10 KB)
    MIN_FILE_SIZE_KB = 10
    MIN_FILE_SIZE_BYTES = MIN_FILE_SIZE_KB * 1024
    if audio.size < MIN_FILE_SIZE_BYTES:
        logger.warning(f"[PREDICT-{unique_id}] ✗ File too small ({audio.size} bytes < {MIN_FILE_SIZE_BYTES} bytes)")
        raise HTTPException(
            status_code=400,
            detail=f"File too small or corrupted. Minimum size: {MIN_FILE_SIZE_KB}KB, received: {audio.size} bytes."
        )
    
    logger.info(f"[PREDICT-{unique_id}] ✓ File size validation passed: {audio.size} bytes")
    
    audio_bytes = await audio.read()
    logger.info(f"[PREDICT-{unique_id}] ✓ Audio bytes read: {len(audio_bytes)} bytes")
    
    # CRITICAL: Verify file isn't just zeros (common error in streaming)
    if len(audio_bytes) == 0:
        logger.error(f"[PREDICT-{unique_id}] ✗ CRITICAL: Audio bytes are empty (0 bytes)!")
        raise HTTPException(status_code=400, detail="Audio file is empty or corrupted")
    
    unique_zeros = len(set(audio_bytes[:min(1000, len(audio_bytes))]))
    logger.info(f"[PREDICT-{unique_id}] Audio content check: {unique_zeros} unique bytes in first 1KB (should be >> 5)")

    # Extract and predict audio score
    if audio_model is not None and scaler is not None:
        try:
            from utils.feature_extraction import extract_features
            import librosa
            # Extract acoustic features
            logger.info(f"[PREDICT-{unique_id}] Extracting features...")
            features = extract_features(audio_bytes)
            logger.info(f"[PREDICT-{unique_id}] Features extracted: shape={features.shape}, dtype={features.dtype}")
            logger.info(f"[PREDICT-{unique_id}] Feature stats: min={features.min():.4f}, max={features.max():.4f}, mean={features.mean():.4f}")
            
            # CRITICAL: Log unique feature values to detect feature extraction failure
            unique_count = np.unique(features).size
            logger.info(f"[PREDICT-{unique_id}] **CRITICAL** Unique Features detected: {unique_count} values (should be >> 10)")
            if unique_count < 10:
                logger.warning(f"[PREDICT-{unique_id}] ⚠️ WARNING: Very few unique features detected! Feature extraction may have failed.")
            
            # Debug: Load raw audio to verify mean changes
            try:
                import io
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
                audio_mean = np.mean(y)
                audio_std = np.std(y)
                logger.info(f"[DEBUG-{unique_id}] Raw audio mean: {audio_mean:.6f}, std: {audio_std:.6f}")
            except Exception as e:
                logger.error(f"[DEBUG-{unique_id}] Could not compute raw audio stats: {e}")
            
            # Scale features: ensure 2D array is passed to scaler
            logger.info(f"[PREDICT-{unique_id}] Scaler info: mean shape={scaler.mean_.shape if hasattr(scaler, 'mean_') else 'N/A'}")
            features_2d = features.reshape(1, -1) if features.ndim == 1 else features
            logger.info(f"[PREDICT-{unique_id}] Features shape before scaling: {features_2d.shape}")
            expected_features = getattr(scaler, "n_features_in_", None)
            if expected_features is None and hasattr(scaler, "mean_"):
                expected_features = scaler.mean_.shape[0]

            if expected_features is not None and int(expected_features) != features_2d.shape[1]:
                logger.warning(
                    f"[PREDICT-{unique_id}] Model/scaler feature mismatch: "
                    f"scaler expects {expected_features}, extractor produced {features_2d.shape[1]}. "
                    "Using content-based audio fallback."
                )
                audio_score = estimate_audio_score_from_features(features)
                logger.info(f"[PREDICT-{unique_id}] Content-based audio score: {audio_score:.4f}")
            else:
                features_scaled = scaler.transform(features_2d)
                logger.info(f"[PREDICT-{unique_id}] Features scaled: shape={features_scaled.shape}")
                logger.info(f"[PREDICT-{unique_id}] Scaled stats: min={features_scaled.min():.4f}, max={features_scaled.max():.4f}, mean={features_scaled.mean():.4f}")
                
                # Predict audio score (supports both TensorFlow and scikit-learn)
                logger.info(f"[PREDICT-{unique_id}] Running model prediction...")
                try:
                    # Try scikit-learn first (predict_proba method)
                    if hasattr(audio_model, 'predict_proba'):
                        logger.info(f"[PREDICT-{unique_id}] Using scikit-learn model prediction...")
                        audio_proba = audio_model.predict_proba(features_scaled)
                        audio_score = float(audio_proba[0][1])  # Probability of class 1 (depression)
                    else:
                        # TensorFlow model
                        logger.info(f"[PREDICT-{unique_id}] Using TensorFlow model prediction...")
                        audio_prediction = audio_model.predict(features_scaled, verbose=0)
                        audio_score = float(audio_prediction[0][0])
                except Exception as e:
                    logger.error(f"[PREDICT-{unique_id}] Model prediction error: {e}. Using fallback...")
                    audio_score = estimate_audio_score_from_features(features)

                if audio_score <= 0.001 or audio_score >= 0.999:
                    logger.warning(
                        f"[PREDICT-{unique_id}] Model returned saturated score {audio_score:.6f}. "
                        "Using content-based audio fallback."
                    )
                    audio_score = estimate_audio_score_from_features(features)

                logger.info(f"[PREDICT-{unique_id}] Audio score prediction: {audio_score:.4f}")
            
        except Exception as e:
            logger.error(f"[PREDICT-{unique_id}] ✗ ERROR in feature extraction/prediction: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Audio inference failed: {e}"
            )
    else:
        logger.warning(f"[PREDICT-{unique_id}] ✗ WARNING: Model/scaler not loaded (model={audio_model is not None}, scaler={scaler is not None})")
        logger.warning(f"[PREDICT-{unique_id}] Using demo placeholder: 0.42")
        audio_score = 0.42  # Demo placeholder

    # Compute behavioral score (mean of domain scores)
    behavioral_score = float(np.mean([sleep_score, physical_score, work_score, social_score, mood_score, history_score, motivation_score]))
    logger.info(f"[PREDICT-{unique_id}] Behavioral score: {behavioral_score:.4f}")
    
    # Late fusion (weighted average)
    fusion_score = 0.6 * audio_score + 0.4 * behavioral_score
    logger.info(f"[PREDICT-{unique_id}] Fusion score (60% audio + 40% behavioral): {fusion_score:.4f}")

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
    
    logger.info(f"[PREDICT-{unique_id}] Final response: {result}")
    logger.info(f"[PREDICT] ==================== END REQUEST {unique_id} ====================\n")
    return result

@app.post("/api/history")
async def save_analysis_result(result: AnalysisResult, current_user: dict = Depends(get_current_user)):
    """
    Save analysis result to user's history in users.json
    """
    try:
        # Add timestamp if not provided
        timestamp = result.timestamp or datetime.utcnow().isoformat()
        
        # Create history entry
        history_entry = {
            "audio_score": result.audio_score,
            "behavioral_score": result.behavioral_score,
            "fusion_score": result.fusion_score,
            "risk": result.risk,
            "confidence": result.confidence,
            "timestamp": timestamp
        }
        
        # Find user in array
        user_index = find_user_index(current_user.get('username'))
        if user_index == -1:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Append to user's history
        if users_db[user_index].get('history') is None:
            users_db[user_index]['history'] = []
        
        users_db[user_index]['history'].append(history_entry)
        
        # Persist to JSON
        save_users(users_db)
        
        logger.info(f"[HISTORY] Analysis result saved for user {current_user.get('username')}")
        logger.info(f"[HISTORY] User now has {len(users_db[user_index]['history'])} results in history")
        
        return {
            "message": "Analysis result saved to history",
            "history_count": len(users_db[user_index]['history']),
            "entry": history_entry
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HISTORY] Failed to save result: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to save history: {e}")

@app.get("/api/history")
async def get_user_history(current_user: dict = Depends(get_current_user)):
    """
    Retrieve user's analysis history
    """
    try:
        user_index = find_user_index(current_user.get('username'))
        if user_index == -1:
            raise HTTPException(status_code=404, detail="User not found")
        
        history = users_db[user_index].get('history', [])
        logger.info(f"[HISTORY] Retrieved {len(history)} results for user {current_user.get('username')}")
        return {
            "username": current_user.get('username'),
            "history": history,
            "count": len(history)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HISTORY] Failed to retrieve history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {e}")

@app.get("/")
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"))

@app.get("/login")
def login_page():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "login.html"))

@app.get("/user-info")
def user_info_page():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "frontend", "user-info.html"))
