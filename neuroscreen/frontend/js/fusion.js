// NeuroScreen — late fusion engine + API call
//
// To wire to real FastAPI backend, replace runFusion() simulation with:
//
//   const formData = new FormData();
//   formData.append('audio', document.getElementById('audio-file-input').files[0]);
//   formData.append('sleep_score', state.domainScores.sleep);
//   formData.append('physical_score', state.domainScores.physical);
//   formData.append('work_score', state.domainScores.work);
//   formData.append('social_score', state.domainScores.social);
//   formData.append('mood_score', state.domainScores.mood);
//   formData.append('history_score', state.domainScores.history);
//   formData.append('motivation_score', state.domainScores.motivation);
//   const res  = await fetch('/predict', { method: 'POST', body: formData });
//   const data = await res.json();
//   // data: { audio_score, behavioral_score, fusion_score, risk, confidence }

function onFileSelect(e) {
  const f = e.target.files[0];
  if (!f) return;
  // Show file name below input (NEW FEATURE)
const fileNameEl = document.getElementById('audio-file-name');
if (fileNameEl) {
  fileNameEl.textContent = `Selected file: ${f.name}`;
}
  state.fileSelected = true;
  
  console.log(`[AUDIO-SELECT] File selected: ${f.name} (${f.size} bytes)`);
  
  // Update file display with explicit DOM manipulation
  const sel = document.getElementById('file-selected');
  const wrapper = document.getElementById('file-selected-wrapper');
  const sizeKB = (f.size / 1024).toFixed(1);
  
  console.log(`[AUDIO-SELECT] DOM elements found - sel:${!!sel}, wrapper:${!!wrapper}`);
  
  // Show the file selected wrapper with visual feedback
  if (sel) {
    sel.innerHTML = `<strong>✓ File Selected: ${f.name}</strong><br><small>${sizeKB} KB</small>`;
    console.log('[AUDIO-SELECT] Updated file-selected text');
  }
  if (wrapper) {
    wrapper.classList.add('visible');
    console.log('[AUDIO-SELECT] Added visible class to wrapper');
  } else {
    console.warn('[AUDIO-SELECT] ⚠️ WARNING: file-selected-wrapper element not found!');
  }
  
  // Highlight upload zone
  const uz = document.getElementById('upload-zone');
  if (uz) {
    uz.style.borderColor = '#2d5a41';
    uz.style.background = '#f0f6f3';
    console.log('[AUDIO-SELECT] Updated upload zone styling');
  }
  
  // Reset analysis state when a new file is selected
  resetAnalysisState();
  
  console.log(`[AUDIO] File selected: ${f.name} (${sizeKB} KB)`);
}

function removeAudioFile() {
  console.log('[AUDIO-REMOVE] Removing audio file');
  
  // Clear the file input
  const fileInput = document.getElementById('audio-file-input');
  if (fileInput) {
    fileInput.value = '';
    console.log('[AUDIO-REMOVE] Cleared file input');
  }
  
  // Reset state
  state.fileSelected = false;
  
  // Hide the file-selected wrapper
  const wrapper = document.getElementById('file-selected-wrapper');
  if (wrapper) {
    wrapper.classList.remove('visible');
    console.log('[AUDIO-REMOVE] Hidden file-selected wrapper');
  }
  
  // Reset file-selected display
  const sel = document.getElementById('file-selected');
  if (sel) {
    sel.innerHTML = '✓ No file selected';
    console.log('[AUDIO-REMOVE] Reset file-selected text');
  }
  
  // Reset upload zone styling
  const uz = document.getElementById('upload-zone');
  if (uz) {
    uz.style.borderColor = '';
    uz.style.background = '';
    console.log('[AUDIO-REMOVE] Reset upload zone styling');
  }
  
  // Clear any audio_score or progress logs
  const audioScoreEl = document.getElementById('r-audio');
  if (audioScoreEl) {
    audioScoreEl.textContent = '—';
  }
  
  const logBox = document.getElementById('log-box');
  if (logBox) {
    logBox.innerHTML = '';
    logBox.classList.remove('visible');
  }
  
  const resultPanel = document.getElementById('result-panel');
  if (resultPanel) {
    resultPanel.classList.remove('visible');
  }
  
  // Reset analysis state
  resetAnalysisState();
  
  console.log('[AUDIO-REMOVE] ✓ Audio file removed, UI reset');
  // Clear displayed file name (NEW FEATURE)
const fileNameEl = document.getElementById('audio-file-name');
if (fileNameEl) {
  fileNameEl.textContent = '';
}
}

function addLog(box, msg, cls = 'info') {
  const line = document.createElement('div');
  line.className   = `log-line ${cls}`;
  line.textContent = msg;
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
}

async function runFusion() {
  const btn         = document.getElementById('run-btn');
  const logBox      = document.getElementById('log-box');
  const resultPanel = document.getElementById('result-panel');
  const audioFile   = document.getElementById('audio-file-input').files[0];

  // Reset analysis state for new submission
  resetAnalysisState();

  btn.disabled = true;
  logBox.innerHTML = '';
  logBox.classList.add('visible');
  resultPanel.classList.remove('visible');

  if (!audioFile) {
    addLog(logBox, '[ERROR] Upload an audio file before running late analysis.', 'error');
    btn.disabled = false;
    return;
  }

  addLog(logBox, '[INIT] NeuroScreen pipeline starting...', 'info');

  try {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('sleep_score', state.domainScores.sleep || 0);
    formData.append('physical_score', state.domainScores.physical || 0);
    formData.append('work_score', state.domainScores.work || 0);
    formData.append('social_score', state.domainScores.social || 0);
    formData.append('mood_score', state.domainScores.mood || 0);
    formData.append('history_score', state.domainScores.history || 0);
    formData.append('motivation_score', state.domainScores.motivation || 0);

    // Log FormData for debugging
    console.log('[FUSION] FormData prepared:');
    console.log(`  - Audio: ${audioFile.name} (${(audioFile.size / 1024).toFixed(1)} KB)`);
    console.log(`  - Sleep: ${state.domainScores.sleep || 0}`);
    console.log(`  - Physical: ${state.domainScores.physical || 0}`);
    console.log(`  - Work: ${state.domainScores.work || 0}`);
    console.log(`  - Social: ${state.domainScores.social || 0}`);
    console.log(`  - Mood: ${state.domainScores.mood || 0}`);
    
    addLog(logBox, `[SUBMIT] Sending ${audioFile.name} to /predict endpoint...`, 'info');

    const token = localStorage.getItem('token');
    const response = await fetch('/predict', {
      method: 'POST',
      body: formData,
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });

    console.log(`[FUSION] Response status: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[FUSION] ✗ Server error: ${response.status} ${response.statusText}`);
      console.error(`[FUSION] Error details: ${errorText}`);
      throw new Error(`HTTP ${response.status}: ${response.statusText}\n${errorText}`);
    }

    const data = await response.json();
    console.log('[FUSION] ✓ Prediction received:', data);

    // Store response and update state
    state.lastApiResponse = data;
    state.audioScore = data.audio_score;
    state.riskScore = data.fusion_score;
    state.riskCategory = data.risk;
    state.confidence = data.confidence;

    // Update UI with real data
    const audioScoreEl = document.getElementById('r-audio');
    if (audioScoreEl) {
      audioScoreEl.textContent = data.audio_score.toFixed(4);
    }
    
    const behScoreEl = document.getElementById('r-beh');
    if (behScoreEl) {
      behScoreEl.textContent = data.behavioral_score.toFixed(4);
    }
    
    const fusionScoreEl = document.getElementById('r-fusion');
    if (fusionScoreEl) {
      fusionScoreEl.textContent = data.fusion_score.toFixed(4);
    }
    
    const riskEl = document.getElementById('r-risk');
    if (riskEl) {
      riskEl.textContent = data.risk;
      riskEl.className = 'risk-pill risk-' + data.risk.toLowerCase().replace(' ', '-');
    }
    
    const confBar = document.getElementById('conf-bar');
    if (confBar) {
      confBar.style.width = `${data.confidence * 100}%`;
    }
    
    const confVal = document.getElementById('conf-val');
    if (confVal) {
      confVal.textContent = `${(data.confidence * 100).toFixed(1)}%`;
    }

    addLog(logBox, `[AUDIO] Audio score: ${data.audio_score.toFixed(4)}`, 'done');
    addLog(logBox, `[FUSION] Fusion score: ${data.fusion_score.toFixed(4)} → ${data.risk}`, 'done');
    addLog(logBox, '[DONE] Analysis complete.', 'done');
    resultPanel.classList.add('visible');

    // Show the View Analytics button
    const analyticsBtn = document.getElementById('view-analytics-btn');
    if (analyticsBtn) {
      analyticsBtn.style.display = 'block';
    }

    // Record session locally
    state.fusionResults.push({
      audio: data.audio_score,
      beh: data.behavioral_score,
      fusion: data.fusion_score,
      risk: data.risk,
      conf: data.confidence,
      time: new Date()
    });
    updateSessionTable();
    if (state.chartsInit) updateCharts();

    // Save result to backend history
    const historyToken = localStorage.getItem('token');
    if (historyToken) {
      try {
        const historyResponse = await fetch('/api/history', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${historyToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            audio_score: data.audio_score,
            behavioral_score: data.behavioral_score,
            fusion_score: data.fusion_score,
            risk: data.risk,
            confidence: data.confidence,
            timestamp: new Date().toISOString()
          })
        });
        if (historyResponse.ok) {
          addLog(logBox, '[HISTORY] Result saved to your analysis history.', 'info');
        }
      } catch (historyError) {
        console.warn('[HISTORY] Could not save to backend history:', historyError);
      }
    }

  } catch (error) {
    addLog(logBox, `[ERROR] ${error.message}`, 'error');
  }

  btn.disabled = false;
}


function updateSessionTable() {
  const tbody = document.getElementById('session-tbody');
  tbody.innerHTML = '';
  state.fusionResults.forEach((r, i) => {
    const riskStyle = r.risk.includes('High') ? 'color:#c0392b' : r.risk.includes('Mod') ? 'color:#b8860b' : 'color:#2d5a3d';
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td style="font-family:var(--font-mono);font-size:12px">${r.time.toLocaleTimeString()}</td>
      <td>${r.audio.toFixed(3)}</td>
      <td>${r.beh.toFixed(3)}</td>
      <td><strong>${r.fusion.toFixed(3)}</strong></td>
      <td style="${riskStyle};font-weight:600">${r.risk}</td>
      <td style="font-family:var(--font-mono)">${(r.conf * 100).toFixed(0)}%</td>`;
    tbody.appendChild(tr);
  });
}

// Drag-drop
window.addEventListener('DOMContentLoaded', () => {
  const uz = document.getElementById('upload-zone');
  if (!uz) {
    console.warn('[DRAG-DROP] upload-zone element not found in DOM');
    return;
  }
  uz.addEventListener('dragover', e => { 
    e.preventDefault(); 
    if (uz) uz.classList.add('drag'); 
  });
  uz.addEventListener('dragleave', () => {
    if (uz) uz.classList.remove('drag');
  });
  uz.addEventListener('drop', e => {
    e.preventDefault(); 
    if (uz) uz.classList.remove('drag');
    const f = e.dataTransfer.files[0];
    if (f) onFileSelect({ target: { files: [f] } });
  });
});

function goToCharts() {
  // Navigate to the Results & Charts tab
  const chartsTab = document.querySelector('[data-tab="charts"]');
  if (chartsTab) {
    chartsTab.click();
  }
}

// Event listener for View Analytics button
document.addEventListener('DOMContentLoaded', () => {
  const analyticsBtn = document.getElementById('view-analytics-btn');
  if (analyticsBtn) {
    analyticsBtn.addEventListener('click', goToCharts);
  }
});
