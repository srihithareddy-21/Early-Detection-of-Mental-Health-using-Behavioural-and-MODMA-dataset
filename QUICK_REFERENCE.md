# Quick Reference - Testing & Deployment

## 🚀 Quick Start

### Backend
```bash
cd neuroscreen/backend
uvicorn main:app --reload
```
Watch for: `[STARTUP] ✓ Audio model loaded` and `[STARTUP] ✓ Scaler loaded`

### Frontend
Open: `http://localhost:8000`

---

## 🔍 Verify Each Fix

### 1. Audio Score Bug (Upload 3 Different Audio Files)

**Check console output:**
- Should see unique REQUEST IDs (e.g., `REQUEST a1b2c3d4`)
- Each file should show DIFFERENT `audio_mean` values
- Each file should show DIFFERENT `audio_score` predictions
- **NOT** all stuck at 0.42

**Example output:**
```
Audio 1: DEBUG Raw audio mean: 0.001234, Audio score: 0.6234
Audio 2: DEBUG Raw audio mean: -0.002145, Audio score: 0.4891
Audio 3: DEBUG Raw audio mean: 0.000567, Audio score: 0.7123
```

✅ If scores vary per file = BUG FIXED

---

### 2. User Persistence

**Test signup/login cycle:**
1. Sign up: username=`test_user`, email=`test@example.com`, password=`pass123`
2. Check `backend/users.json` exists and contains the user
3. Close browser / Refresh page
4. Login with same credentials
5. Should log in successfully

✅ If login works after refresh = PERSISTENCE WORKING

---

### 3. Profile Modal

**Test edit profile:**
1. Click profile icon (👤) in top-right header
2. Modal opens showing: Username, Email, Name, Age, Gender
3. Click [Edit] button
4. Update Name, Age, Gender
5. Click [Save]
6. Should see "Profile updated successfully!"
7. Refresh page - profile changes persist

✅ If profile saves and persists = MODAL WORKING

---

### 4. UI Cleanup

**Visual checks:**
- [ ] Audio + Fusion tab shows 4 domain chips (not 5)
- [ ] Energy card is gone
- [ ] Overview tab shows clinical disclaimer
- [ ] Results & Charts shows pie chart (Risk vs Healthy) and bar chart
- [ ] Tab bar has: Overview, Questionnaire, Audio+Fusion, Results&Charts, About (5 tabs)

✅ All checks passing = UI CLEANED UP

---

## 📊 Sample Test Data

### For Testing Audio Upload
You can use any .wav file or create test audio:
- Use voice recorder on phone
- Keep it 30-120 seconds
- Different audio files will produce different scores

### For Testing Questionnaire
All scores work (0-4 scale). Example:
- Sleep: 2
- Physical: 1
- Work: 3
- Social: 2
- Mood: 4
- History: 2
- Motivation: 1

---

## 🐛 Troubleshooting

### If Audio Score Still 0.42
1. Check console for `[STARTUP] ✗ Scaler NOT found`
2. Verify file exists: `backend/models/audio_scaler.pkl`
3. Check feature extraction isn't throwing errors
4. Look for exception in `[PREDICT] ERROR in feature extraction`

### If Login Fails After Signup
1. Check `backend/users.json` exists
2. Verify user data is saved: `cat backend/users.json`
3. Check password hashing working (bcrypt)
4. Look for `[LOGIN_FAIL]` in console

### If Profile Modal Won't Save
1. Check token is in localStorage
2. Verify `/api/user-info` endpoint accessible
3. Check `[USER_UPDATE]` log in backend console
4. Verify users.json updated after save

### If Charts Don't Update
1. Run an analysis first
2. Check `state.fusionResults` contains data
3. Verify `updateCharts()` is called
4. Check Chart.js library loaded

---

## 📝 Files Modified

### Backend
- ✅ `backend/main.py` - Audio fix + JSON persistence + logging
- ✅ `backend/utils/feature_extraction.py` - Enhanced logging + error handling
- 🆕 `backend/users.json` - Created on first signup

### Frontend
- ✅ `frontend/index.html` - Profile modal HTML + functions
- ✅ `frontend/login.html` - Simplified login flow
- ✅ `frontend/css/style.css` - Modal styling
- ✅ `frontend/js/charts.js` - Verified (no changes needed)

---

## ✅ Pre-Deployment Checklist

Before going live:

1. [ ] Backend starts without errors
2. [ ] Audio scores vary (tested 3+ files)
3. [ ] Users persist (signup/login cycle works)
4. [ ] Profile modal works (edit/save works)
5. [ ] UI clean (no Energy card, disclaimer visible)
6. [ ] Charts update dynamically
7. [ ] Console shows detailed logs
8. [ ] No broken links or 404s
9. [ ] Token stored in localStorage
10. [ ] All tabs navigate correctly

---

## 🎯 Key Metrics to Monitor

### Performance
- Audio prediction time: < 1 second
- File upload time: < 3 seconds
- Profile save time: < 500ms

### Reliability
- Zero 0.42 predictions (all should vary)
- 100% user login success rate (with correct password)
- Profile updates persist across sessions

### User Experience
- Clear error messages
- Modal responsive and smooth
- Charts update instantly
- All buttons responsive

---

## 📞 Support

If issues occur:
1. Check console logs (browser F12 + backend terminal)
2. Verify file paths are correct
3. Restart backend server
4. Clear browser cache (Ctrl+Shift+Del)
5. Check users.json is readable/writable

All systems ready for final deployment! 🚀
