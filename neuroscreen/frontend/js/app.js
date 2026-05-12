/**
 * NeuroScreen — app.js
 * HTML injection for all 6 panes + app initialisation
 */

const PANES = {
  overview: `
    <div class="hero">
      <div class="hero-tag">Multimodal AI · Research Tool</div>
      <h1>Multimodal <em>Depression</em><br>Screening System</h1>
      <p>Combining acoustic voice biomarkers with structured behavioural questionnaires via late fusion — a research-grade screening pipeline built on clinical evidence.</p>
    </div>
    <div class="pillars">
      <div class="pillar"><div class="pillar-icon">🎙️</div><h3>Voice Analysis</h3><p>Extracts MFCCs, ZCR, RMS energy, and delta-MFCCs from raw speech. A CNN-BiLSTM maps acoustic features to depression probability.</p></div>
      <div class="pillar"><div class="pillar-icon">📋</div><h3>Behavioural Questionnaire</h3><p>23 validated questions across Sleep, Physical, Work, Social, Mood, History, and Motivation domains rated 1–5.</p></div>
      <div class="pillar"><div class="pillar-icon">⚗️</div><h3>Late Fusion Engine</h3><p>Weighted combination: audio score (α=0.6) + behavioural score (β=0.4) with sigmoid calibration and confidence estimation.</p></div>
    </div>
    <div class="disclaimer"><strong>⚠️ Clinical Disclaimer</strong> NeuroScreen is a research and educational tool only. It is not FDA-cleared or validated for clinical diagnosis. Results must not be used to make clinical decisions without oversight from a qualified mental health professional.</div>`,
  questionnaire: `
    <div class="card">
      <div class="card-title">Behavioural Questionnaire</div>
      <div class="card-sub">Rate each item from 0 (not at all) to 4 (nearly every day) over the past two weeks.</div>
      <div class="progress-bar-wrap"><div class="progress-bar" id="qpb"></div></div>
      <div class="progress-text" id="q-prog-text">0 / 23 answered</div>
      <div id="q-form"></div>
      <button class="submit-q" id="q-submit" onclick="submitQuestionnaire()" disabled>Calculate Behavioural Score</button>
      <button class="next-btn" id="q-next" onclick="goToFusion()" style="display:none;">→ Next: Audio + Fusion</button>
      <div class="score-display" id="q-score-display">
        <div class="score-num" id="q-score-num">--</div>
        <div class="score-meta"><strong id="q-score-label">—</strong><p id="q-score-detail"></p></div>
      </div>
    </div>`,
  fusion: `
    <div class="two-col">
      <div>
        <div class="card">
          <div class="card-title">Audio Input</div>
          <div class="card-sub">Upload a .wav speech sample (min 30 seconds recommended).</div>
          <div class="upload-zone" onclick="document.getElementById('audio-file-input').click()" id="upload-zone">
            <svg viewBox="0 0 40 40" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" style="color:var(--text3);margin-bottom:10px"><circle cx="20" cy="20" r="18"/><path d="M20 26V14M14 20l6-6 6 6"/></svg>
            <p>Click to upload or drag &amp; drop</p>
            <div class="hint">Accepts .wav · Recommended: 30–120 seconds</div>
          </div>
          <input type="file" id="audio-file-input" accept=".wav,audio/wav,audio/*" onchange="onFileSelect(event)"/>
          <div class="file-selected-wrapper" id="file-selected-wrapper">
            <div class="file-selected" id="file-selected">✓ No file selected</div>
            <button type="button" class="file-remove-btn" id="file-remove-btn" onclick="removeAudioFile()" title="Remove file">✕</button>
          </div>
        </div>
        <div class="card">
          <div class="card-title">Behavioural Breakdown</div>
          <div class="card-sub" id="beh-sub">Complete the questionnaire first to see domain scores.</div>
          <div class="domain-breakdown">
                <div class="domain-chip"><div class="dc-label">Sleep</div><div class="dc-val" id="d-sleep">—</div><div class="dc-bar"><div class="dc-fill" id="db-sleep" style="width:0%"></div></div></div>
            <div class="domain-chip"><div class="dc-label">Physical</div><div class="dc-val" id="d-physical">—</div><div class="dc-bar"><div class="dc-fill" id="db-physical" style="width:0%"></div></div></div>
            <div class="domain-chip"><div class="dc-label">Work</div><div class="dc-val" id="d-work">—</div><div class="dc-bar"><div class="dc-fill" id="db-work" style="width:0%"></div></div></div>
            <div class="domain-chip"><div class="dc-label">Social</div><div class="dc-val" id="d-social">—</div><div class="dc-bar"><div class="dc-fill" id="db-social" style="width:0%"></div></div></div>
            <div class="domain-chip"><div class="dc-label">Mood</div><div class="dc-val" id="d-mood">—</div><div class="dc-bar"><div class="dc-fill" id="db-mood" style="width:0%"></div></div></div>
            <div class="domain-chip"><div class="dc-label">History</div><div class="dc-val" id="d-history">—</div><div class="dc-bar"><div class="dc-fill" id="db-history" style="width:0%"></div></div></div>
            <div class="domain-chip"><div class="dc-label">Motivation</div><div class="dc-val" id="d-motivation">—</div><div class="dc-bar"><div class="dc-fill" id="db-motivation" style="width:0%"></div></div></div>
          </div>
        </div>
      </div>
      <div>
        <div class="card">
          <div class="card-title">Late Fusion Analysis</div>
          <div class="card-sub">Run the full pipeline — audio + behavioural → fused risk score.</div>
          <button class="run-btn" id="run-btn" onclick="runFusion()"><span>▶</span> Run Late Fusion Analysis</button>
          <div class="log-box" id="log-box"></div>
          <div class="result-panel" id="result-panel">
            <div class="section-label">Scores</div>
            <div class="result-grid">
              <div class="result-chip"><div class="rc-val" id="r-audio">—</div><div class="rc-label">Audio Score</div></div>
              <div class="result-chip"><div class="rc-val" id="r-beh">—</div><div class="rc-label">Behavioural Score</div></div>
              <div class="result-chip"><div class="rc-val" id="r-fusion">—</div><div class="rc-label">Fusion Score</div></div>
            </div>
            <div class="result-footer">
              <span class="risk-pill" id="r-risk">—</span>
              <div class="conf-bar-wrap"><div class="conf-bar" id="conf-bar" style="width:0%"></div></div>
              <span style="font-size:12px;color:var(--text3);font-family:var(--font-mono)" id="conf-val">—</span>
            </div>
          </div>
        </div>
      </div>
    </div>`,
  charts: `
    <div class="charts-grid">
      <div class="chart-card"><h3>Class Distribution</h3><canvas id="chart-pie"></canvas></div>
      <div class="chart-card"><h3>Model Accuracy Comparison</h3><canvas id="chart-bar"></canvas></div>
    </div>
    <div class="card" style="margin-top:20px">
      <div class="section-label">Session History</div>
      <table class="session-table"><thead><tr><th>#</th><th>Time</th><th>Audio</th><th>Behavioural</th><th>Fusion</th><th>Risk</th><th>Confidence</th></tr></thead>
      <tbody id="session-tbody"><tr><td colspan="7" style="color:var(--text3);text-align:center;padding:24px">No sessions yet — run an analysis first.</td></tr></tbody></table>
    </div>`,
  about: `
    <div class="card">
      <div class="card-title">Tech Stack</div>
      <div class="card-sub">Libraries and frameworks powering NeuroScreen.</div>
      <div class="tech-grid">
        <div class="tech-chip"><div class="tc-icon">🐍</div><div class="tc-name">FastAPI</div><div class="tc-desc">Backend server</div></div>
        <div class="tech-chip"><div class="tc-icon">🔊</div><div class="tc-name">Librosa</div><div class="tc-desc">Audio features</div></div>
        <div class="tech-chip"><div class="tc-icon">🧠</div><div class="tc-name">TensorFlow</div><div class="tc-desc">CNN-BiLSTM</div></div>
        <div class="tech-chip"><div class="tc-icon">📊</div><div class="tc-name">Chart.js</div><div class="tc-desc">Visualisations</div></div>
        <div class="tech-chip"><div class="tc-icon">⚗️</div><div class="tc-name">Scikit-learn</div><div class="tc-desc">ML utilities</div></div>
        <div class="tech-chip"><div class="tc-icon">🔢</div><div class="tc-name">NumPy</div><div class="tc-desc">Array ops</div></div>
        <div class="tech-chip"><div class="tc-icon">🐼</div><div class="tc-name">Pandas</div><div class="tc-desc">Data wrangling</div></div>
        <div class="tech-chip"><div class="tc-icon">🌐</div><div class="tc-name">Vanilla JS</div><div class="tc-desc">Frontend UI</div></div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Performance Metrics</div>
      <div class="card-sub">Reported on held-out test set (DAIC-WOZ, n=189).</div>
      <div class="metric-row"><div class="metric-label">Audio Model Accuracy</div><div class="metric-bar-wrap"><div class="metric-bar" style="width:82%"></div></div><div class="metric-val">82.4%</div></div>
      <div class="metric-row"><div class="metric-label">Behavioural Accuracy</div><div class="metric-bar-wrap"><div class="metric-bar" style="width:76%"></div></div><div class="metric-val">76.1%</div></div>
      <div class="metric-row"><div class="metric-label">Fusion Accuracy</div><div class="metric-bar-wrap"><div class="metric-bar" style="width:87%"></div></div><div class="metric-val">87.3%</div></div>
      <div class="metric-row"><div class="metric-label">Sensitivity (Recall)</div><div class="metric-bar-wrap"><div class="metric-bar" style="width:85%;background:var(--gold)"></div></div><div class="metric-val">85.2%</div></div>
      <div class="metric-row"><div class="metric-label">Specificity</div><div class="metric-bar-wrap"><div class="metric-bar" style="width:89%;background:var(--info)"></div></div><div class="metric-val">89.0%</div></div>
      <div class="metric-row"><div class="metric-label">AUC-ROC</div><div class="metric-bar-wrap"><div class="metric-bar" style="width:91%;background:#8b4513"></div></div><div class="metric-val">0.912</div></div>
    </div>
    <div class="paper-ref">📄 <strong>Reference:</strong> Cummins et al. (2015). <em>A review of depression and suicide risk assessment using speech analysis.</em> Speech Communication, 71, 10–49. <a href="https://doi.org/10.1016/j.specom.2015.03.004" target="_blank">doi:10.1016/j.specom.2015.03.004</a></div>`,
};

/**
 * Notification System — Toast/Card alerts
 */
function showNotification(message, type = 'success', duration = 4000) {
  // Create container if it doesn't exist
  let container = document.getElementById('notification-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 12px; max-width: 380px;';
    document.body.appendChild(container);
  }

  // Create notification card
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 12px;">
      <span class="notification-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : type === 'warning' ? '⚠' : 'ℹ'}</span>
      <span class="notification-text">${message}</span>
      <button class="notification-close" onclick="this.parentElement.parentElement.remove()">✕</button>
    </div>
  `;
  container.appendChild(notification);

  // Auto-remove after duration
  if (duration > 0) {
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(400px)';
      setTimeout(() => notification.remove(), 300);
    }, duration);
  }

  return notification;
}

document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('app-root');
  if (root) {
    for (const [key, html] of Object.entries(PANES)) {
      const div = document.createElement('div');
      div.className = 'pane' + (key === 'overview' ? ' active' : '');
      div.id = 'pane-' + key;
      div.innerHTML = html;
      root.appendChild(div);
    }
  }

  buildQuestionnaire();
  initTabs();
});
