# Complete Testing & Verification Guide

## 🧪 Quick Test Protocol

### BEFORE YOU START:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Keep DevTools visible during testing
4. Watch for [AUDIO], [FUSION], [PROFILE] log messages

---

## TEST 1: Audio File Selection ✅

**Steps:**
1. Go to "Audio + Fusion" tab
2. Click upload zone (or drag-drop a .wav file)
3. Select any audio file (30+ seconds recommended)

**Expected Console Logs:**
```
[AUDIO-SELECT] File selected: {filename} ({size} bytes)
[AUDIO-SELECT] DOM elements found - sel:true, wrapper:true
[AUDIO-SELECT] Updated file-selected text
[AUDIO-SELECT] Added visible class to wrapper
[AUDIO-SELECT] Updated upload zone styling
[AUDIO] File selected: {filename} ({sizeKB} KB)
```

**Expected UI Changes:**
- ✓ Upload zone now shows: "✓ File Selected: filename"
- ✓ File size displayed below filename
- ✓ Upload zone background highlights green (#f0f6f3)
- ✓ Remove button (✕) appears next to filename
- ✓ [Remove] button click resets UI back to "Click to upload"

**If It Fails:**
```
❌ No UI update after upload
→ Check: DOM elements found - sel:false or wrapper:false?
→ Solution: Check if HTML panes are properly loaded

❌ Console shows error in onFileSelect
→ Check: Is fusion.js properly loaded?
→ Try: Refresh page and check DevTools Network tab
```

---

## TEST 2: Complete Questionnaire ✅

**Steps:**
1. Go to "Questionnaire" tab
2. Answer all 23 questions (rate 0-4)
3. Click "Calculate Behavioral Score"

**Expected Result:**
- Score displays (e.g., 0.35)
- Domain scores show below (Sleep: 0.30, Mood: 0.64, etc.)
- "Proceed to Audio Analysis" button appears

**Console Should Show:**
```
[QUESTIONNAIRE] Calculating behavioral score...
[SCORES] Domain scores calculated: {scores}
[SUBMIT] Behavioral score: 0.51
```

---

## TEST 3: Run Fusion Analysis ✅ CRITICAL

**Prerequisites:**
- Audio file uploaded ✓
- Questionnaire completed ✓

**Steps:**
1. Go to "Audio + Fusion" tab
2. Verify file is showing in upload section
3. Verify behavioral scores showing (Sleep, Mood, Social, Physical)
4. Click "▶ Run Late Fusion Analysis"

**Watch Console for:**
```
[FUSION] FormData prepared:
  - Audio: {filename} ({size} KB)
  - Sleep: 0.30
  - Physical: 0.60
  - Work: ...
  - Social: 0.50
  - Mood: 0.64
[SUBMIT] Sending {filename} to /predict endpoint...
[FUSION] Response status: 200
[FUSION] ✓ Prediction received: {data}
[AUDIO] Audio score: 0.68 ← This should NOT be 0.42
[FUSION] Fusion score: 0.62 → Moderate Risk
[DONE] Analysis complete.
```

**Backend Console Should Show:**
```
[PREDICT-abc123] ==================== REQUEST abc123 ====================
[PREDICT-abc123] User: {username}
[PREDICT-abc123] Audio file: {filename} (245120 bytes)
[PREDICT-abc123] ✓ File size validation passed: 245120 bytes
[PREDICT-abc123] ✓ Audio bytes read: 245120 bytes
[PREDICT-abc123] Audio content: 247 unique bytes (should be >> 5)
[PREDICT-abc123] TensorFlow session cleared
[PREDICT-abc123] Extracting features...
[PREDICT-abc123] **CRITICAL** Unique Features: 164 values (should be >> 10)
[PREDICT-abc123] ✓ Audio score prediction: 0.68
[PREDICT-abc123] Behavioral score: 0.51
[PREDICT-abc123] Fusion score: 0.62 (60% audio + 40% behavioral)
```

**Expected UI Result:**
```
Scores:
  Audio Score: 0.6824 ← REAL prediction
  Behavioral Score: 0.5100
  Fusion Score: 0.6122

Risk: Moderate Risk (green bar at ~62%)
Confidence: 82.3%

Session History table updated with new row
```

**If Audio Score is Still 0.42:**
```
❌ Audio Score: 0.42 (fallback value)
→ Check backend logs for error: [PREDICT] ✗ ERROR
→ Verify file size: should be > 10KB
→ Verify unique features: should be >> 10
→ Check TensorFlow session cleared message
```

**If "Error: File too small" appears:**
```
❌ HTTP 400: File too small or corrupted
→ Your audio file is < 10KB
→ Select a longer audio file (30+ seconds = ~500KB)
```

---

## TEST 4: History Persistence ✅

**After running analysis:**
1. Check console for:
```
[HISTORY] Result saved to your analysis history.
```

2. Stop backend server
3. Delete `/neuroscreen/backend/users.json`
4. Restart backend server
5. Login again
6. Go to "Results & Charts" tab
7. Check Session History table - previous result should still be there

**In users.json, verify entry exists:**
```json
{
  "username": "octopus",
  "history": [
    {
      "audio_score": 0.6824,
      "behavioral_score": 0.51,
      "fusion_score": 0.6122,
      "risk": "Moderate Risk",
      "confidence": 0.8234,
      "timestamp": "2026-04-22T14:30:45.123456"
    }
  ]
}
```

---

## TEST 5: Profile Update Notification ✅

**Steps:**
1. Click profile icon (👤) in top-right
2. Click "Edit Profile" button
3. Change name, age, or gender
4. Click "Save Changes"

**Expected UI:**
- Green toast card slides in from top-right
- Message: "✓ Profile updated successfully!"
- Stays for 3 seconds then auto-dismisses
- OR click X to manually close

**Expected Console:**
```
[PROFILE] Notification shown
```

**If Alert Dialog Appears Instead:**
```
❌ Browser alert() dialog shows
→ Check: typeof showNotification in console
→ Verify notification-container div exists in HTML
→ Check: Is function defined globally?
→ Reload page if scripts not loaded
```

**Test Error Notification:**
1. Try to save profile with INVALID data (if validation exists)
2. Should show RED error card instead
3. Message: "✗ Error updating profile: ..."

---

## TEST 6: Edge Cases ✅

### Edge Case A: Empty File
```javascript
// In console, manually upload 0-byte file
// Expected: [PREDICT-id] ✗ CRITICAL: Audio bytes are empty!
// Error: "Audio file is empty or corrupted"
```

### Edge Case B: Very Small File
```
// Upload a 5KB file
// Expected: File too small error
// Message: "Minimum size: 10KB, received: 5120 bytes"
```

### Edge Case C: Network Error
```
// Simulate offline mode (DevTools Network tab → Offline)
// Try to run analysis
// Expected: [ERROR] Failed to fetch (network error shown in logs)
```

### Edge Case D: Remove File and Re-Upload
```
1. Upload file → shows "✓ File Selected: audio.wav"
2. Click Remove button (✕)
3. Verify UI resets to "Click to upload or drag & drop"
4. Upload different file → should update UI with new filename
5. Expected: No errors, clean state transition
```

---

## 🔍 Diagnostic Checklist

| Issue | Diagnostic | Fix |
|-------|-----------|-----|
| Audio file doesn't show | Check `[AUDIO-SELECT]` logs | Verify wrapper element in HTML |
| Audio score is 0.42 | Check `[PREDICT-id]` backend logs | Verify file size > 10KB, unique features >> 10 |
| Notification not showing | Type `showNotification` in console | Check if function is undefined |
| History not saving | Check `[HISTORY]` logs | Verify /api/history endpoint working |
| Form validation fails | Check browser DevTools | Verify input fields have required attributes |

---

## 📋 Sign-Off Checklist

- [ ] Audio file upload shows "✓ File Selected: filename (size KB)"
- [ ] Audio file can be removed with ✕ button
- [ ] Audio score in results is NOT 0.42 (shows real value like 0.68)
- [ ] Behavioral scores calculate from questionnaire
- [ ] Fusion score combines audio (60%) + behavioral (40%)
- [ ] Risk category shows correctly (Low/Moderate/High)
- [ ] Confidence bar displays (0-100%)
- [ ] Green toast notification shows on profile update
- [ ] Toast automatically disappears after 3 seconds
- [ ] Session history table updates after each analysis
- [ ] Results persist in users.json
- [ ] Backend logs show [PREDICT-id] prefix on all messages
- [ ] No console errors (only expected logs)
- [ ] Form validation prevents incomplete submissions

---

## 🆘 Emergency Troubleshooting

### If nothing works:
1. **Clear browser cache:** Ctrl+Shift+Delete → Clear all
2. **Hard refresh:** Ctrl+F5 (not just F5)
3. **Check file size:** Your test file must be > 10KB
4. **Check backend:** Is `uvicorn main:app --reload` running?
5. **Check firewall:** Can browser reach http://127.0.0.1:8000?

### If backend shows errors:
1. **Install dependencies:** `pip install -r requirements.txt`
2. **Check TensorFlow:** `python -c "import tensorflow; print(tensorflow.__version__)"`
3. **Check models:** Do `models/audio_model.h5` and `models/audio_scaler.pkl` exist?
4. **Restart backend:** Stop and `uvicorn main:app --reload`

### If database issues:
1. **Delete and recreate:** `rm backend/users.json`
2. **Check permissions:** Can Python write to backend directory?
3. **Verify JSON:** Open `users.json` and check it's valid JSON

---

## ✅ Final Verification

```
Backend Console:
✓ [STARTUP] Loaded X users from users.json
✓ [PREDICT-id] ✓ Audio score prediction: 0.XX
✓ [HISTORY] Analysis result saved to history

Browser Console:
✓ [AUDIO-SELECT] File selected: filename
✓ [FUSION] FormData prepared
✓ [FUSION] ✓ Prediction received
✓ [PROFILE] Notification shown

UI:
✓ File upload shows filename
✓ Audio score is NOT 0.42
✓ Toast notification appears
✓ History table updates
```

**If all checkmarks present → 🟢 READY FOR PRODUCTION**

---

**Test Date:** 2026-04-22  
**Tester:** [Your Name]  
**Status:** ✓ Pass / ❌ Fail
