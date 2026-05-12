// NeuroScreen — 12-question form logic

function buildQuestionnaire() {
  const form = document.getElementById('q-form');
  let currentDomain = null;
  let html = '';

  QUESTIONS.forEach((q, idx) => {
    if (q.domain !== currentDomain) {
      currentDomain = q.domain;
      const name = currentDomain.charAt(0).toUpperCase() + currentDomain.slice(1);
      html += `<div class="domain-label ${DOMAIN_COLOR[q.domain]}">${DOMAIN_EMOJI[q.domain]} ${name} Domain</div>`;
    }
    html += `<div class="question-block" id="qb-${q.id}">
      <div class="question-text-with-reset">
        <span>${idx + 1}. ${q.text}</span>
        <button type="button" class="q-reset-btn" onclick="clearQuestion('${q.id}')" title="Reset this answer">⟲</button>
      </div>
      <div class="options" id="opts-${q.id}">`;
    OPTS.forEach(o => {
      html += `<label class="option-label" id="ol-${q.id}-${o.val}">
        <input type="radio" name="${q.id}" value="${o.val}" onchange="onAnswer('${q.id}', ${o.val}, this)"/>
        ${o.label}
        <span class="q-score-badge">${o.val}</span>
      </label>`;
    });
    html += `</div></div>`;
  });

  form.innerHTML = html;
}

function clearQuestion(qid) {
  // Remove the answer from state
  delete state.answers[qid];
  
  // Deselect all radio buttons for this question
  document.querySelectorAll(`input[name="${qid}"]`).forEach(input => {
    input.checked = false;
  });
  
  // Remove selection styling
  document.querySelectorAll(`#opts-${qid} .option-label`).forEach(l => l.classList.remove('selected'));
  
  // Update progress
  updateProgress();
  
  // Hide the Next button if the user clears an answer after submitting
  const nextBtn = document.getElementById('q-next');
  if (nextBtn && nextBtn.style.display === 'block') {
    nextBtn.style.display = 'none';
    document.getElementById('q-score-display').classList.remove('visible');
  }
}

function clearAllAnswers() {
  // Confirm before clearing
  if (!confirm('Are you sure you want to clear all answers? This action cannot be undone.')) {
    return;
  }
  
  // Clear state
  state.answers = {};
  state.domainScores = { sleep: null, physical: null, work: null, social: null, mood: null, history: null, motivation: null };
  state.behavioralScore = null;
  
  // Clear all radio buttons
  document.querySelectorAll('input[type="radio"]').forEach(input => {
    input.checked = false;
  });
  
  // Remove all selection styling
  document.querySelectorAll('.option-label.selected').forEach(l => l.classList.remove('selected'));
  
  // Hide score display and next button
  document.getElementById('q-score-display').classList.remove('visible');
  const nextBtn = document.getElementById('q-next');
  if (nextBtn) {
    nextBtn.style.display = 'none';
  }
  
  // Update progress
  updateProgress();
}

function onAnswer(qid, val, el) {
  state.answers[qid] = val;
  document.querySelectorAll(`#opts-${qid} .option-label`).forEach(l => l.classList.remove('selected'));
  el.closest('.option-label').classList.add('selected');
  updateProgress();
  // Hide the Next button if the user changes their answer after submitting
  const nextBtn = document.getElementById('q-next');
  if (nextBtn && nextBtn.style.display === 'block') {
    nextBtn.style.display = 'none';
    document.getElementById('q-score-display').classList.remove('visible');
  }
}

function updateProgress() {
  const answered = Object.keys(state.answers).length;
  const pct = (answered / 23) * 100;
  document.getElementById('qpb').style.width = pct + '%';
  document.getElementById('q-prog-text').textContent = `${answered} / 23 answered`;
  document.getElementById('q-submit').disabled = answered < 23;
}

function submitQuestionnaire() {
  let total = 0;
  for (const [domain, ids] of Object.entries(DOMAIN_QUESTIONS)) {
    const sum = ids.reduce((a, id) => a + (state.answers[id] || 0), 0);
    state.domainScores[domain] = sum / (ids.length * 5);
    total += sum;
  }
  state.behavioralScore = total / (23 * 5);
  const rawTotal = total;

  let label = 'Minimal';
  if      (rawTotal >= 80) label = 'Severe';
  else if (rawTotal >= 60) label = 'Moderately Severe';
  else if (rawTotal >= 40) label = 'Moderate';
  else if (rawTotal >= 20) label = 'Mild';

  const disp = document.getElementById('q-score-display');
  disp.classList.add('visible');
  document.getElementById('q-score-num').textContent   = rawTotal;
  document.getElementById('q-score-label').textContent = `${label} (${rawTotal}/115)`;
  document.getElementById('q-score-detail').textContent = `Normalized behavioral score: ${state.behavioralScore.toFixed(3)}`;

  // Show the Next button after calculation
  const nextBtn = document.getElementById('q-next');
  if (nextBtn) {
    nextBtn.style.display = 'block';
  }

  updateDomainDisplay();
}

function goToFusion() {
  // Navigate to the Audio + Fusion tab
  const fusionTab = document.querySelector('[data-tab="fusion"]');
  if (fusionTab) {
    fusionTab.click();
  }
}

function updateDomainDisplay() {
  if (!state.domainScores.sleep) return;
  for (const d of Object.keys(DOMAIN_QUESTIONS)) {
    const v = state.domainScores[d];
    const el = document.getElementById(`d-${d}`);
    const bar = document.getElementById(`db-${d}`);
    if (el) el.textContent = v.toFixed(2);
    if (bar) bar.style.width = (v * 100) + '%';
  }
  document.getElementById('beh-sub').textContent = 'Domain scores computed from questionnaire responses.';
}
