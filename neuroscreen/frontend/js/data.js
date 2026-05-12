// NeuroScreen — questions, state, constants

const QUESTIONS = [
  { id: 'q1',  domain: 'sleep',      text: 'How many hours of sleep do you get per night?' },
  { id: 'q2',  domain: 'sleep',      text: 'Do you follow a regular sleep schedule?' },
  { id: 'q3',  domain: 'physical',   text: 'How often do you exercise?' },
  { id: 'q4',  domain: 'physical',   text: 'How many hours per day do you spend on social media or screen time?' },
  { id: 'q5',  domain: 'physical',   text: 'How often do you consume alcohol or smoke?' },
  { id: 'q6',  domain: 'work',       text: 'How often do you feel work or academic pressure?' },
  { id: 'q7',  domain: 'work',       text: 'Do you feel that your workload is manageable?' },
  { id: 'q8',  domain: 'work',       text: 'Do you experience difficulty relaxing after work or study?' },
  { id: 'q9',  domain: 'social',     text: 'Do you feel comfortable talking to people around you?' },
  { id: 'q10', domain: 'social',     text: 'Do you avoid social gatherings?' },
  { id: 'q11', domain: 'social',     text: 'Do you feel lonely even when around others?' },
  { id: 'q12', domain: 'social',     text: 'Do you feel supported by friends or family?' },
  { id: 'q13', domain: 'mood',       text: 'Do you often feel sad or hopeless?' },
  { id: 'q14', domain: 'mood',       text: 'Do you feel stressed or overwhelmed frequently?' },
  { id: 'q15', domain: 'mood',       text: 'Do you lose interest in activities you usually enjoy?' },
  { id: 'q16', domain: 'mood',       text: 'Do you find it difficult to concentrate on tasks?' },
  { id: 'q17', domain: 'mood',       text: 'Do you feel tired or low energy most of the time?' },
  { id: 'q18', domain: 'history',    text: 'Have you ever been diagnosed with a mental health condition?' },
  { id: 'q19', domain: 'history',    text: 'Have you ever consulted a psychologist or psychiatrist?' },
  { id: 'q20', domain: 'history',    text: 'Is there a family history of mental health disorders?' },
  { id: 'q21', domain: 'motivation', text: 'Do you find it difficult to start daily tasks?' },
  { id: 'q22', domain: 'motivation', text: 'Do you often feel unmotivated or mentally exhausted?' },
  { id: 'q23', domain: 'motivation', text: 'Do you experience sudden mood changes?' },
];

const OPTS = [
  { val: 1, label: 'Not at all' },
  { val: 2, label: 'Slightly' },
  { val: 3, label: 'Moderately' },
  { val: 4, label: 'Quite a bit' },
  { val: 5, label: 'Very much' },
];

const DOMAIN_QUESTIONS = {
  sleep:      ['q1', 'q2'],
  physical:   ['q3', 'q4', 'q5'],
  work:       ['q6', 'q7', 'q8'],
  social:     ['q9', 'q10', 'q11', 'q12'],
  mood:       ['q13', 'q14', 'q15', 'q16', 'q17'],
  history:    ['q18', 'q19', 'q20'],
  motivation: ['q21', 'q22', 'q23'],
};

const DOMAIN_COLOR  = { 
  sleep: 'domain-sleep', 
  physical: 'domain-physical', 
  work: 'domain-work', 
  social: 'domain-social', 
  mood: 'domain-mood', 
  history: 'domain-history', 
  motivation: 'domain-motivation' 
};
const DOMAIN_EMOJI  = { 
  sleep: '😴', 
  physical: '🏃', 
  work: '💼', 
  social: '🤝', 
  mood: '💭', 
  history: '📜', 
  motivation: '🚀' 
};

// Fusion weights
const AUDIO_WEIGHT      = 0.6;
const BEHAVIORAL_WEIGHT = 0.4;

// App state
const state = {
  answers: {},
  domainScores: { sleep: null, physical: null, work: null, social: null, mood: null, history: null, motivation: null },
  behavioralScore: null,
  audioScore: null,
  riskScore: null,
  riskCategory: null,
  confidence: null,
  fusionResults: [],
  fileSelected: false,
  chartsInit: false,
  lastApiResponse: null,
  chartInstances: {},
};

// State reset function for new submission
function resetAnalysisState() {
  state.audioScore = null;
  state.riskScore = null;
  state.riskCategory = null;
  state.confidence = null;
  state.lastApiResponse = null;
  // Hide the View Analytics button
  const analyticsBtn = document.getElementById('view-analytics-btn');
  if (analyticsBtn) {
    analyticsBtn.style.display = 'none';
  }
}
