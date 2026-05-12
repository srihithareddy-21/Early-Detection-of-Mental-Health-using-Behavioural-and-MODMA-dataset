// NeuroScreen — pie, bar & hbar Chart.js charts

function initCharts() {
  if (state.chartsInit) return;
  state.chartsInit = true;

  Chart.defaults.font  = { family: 'Outfit, sans-serif', size: 12 };
  Chart.defaults.color = '#6b6560';

  state.chartInstances.pie = new Chart(document.getElementById('chart-pie'), {
    type: 'doughnut',
    data: {
      labels: ['Healthy/Baseline', 'Risk/Probability'],
      datasets: [{
        data: [0, 0],
        backgroundColor: ['#2d5a3d', '#c0392b'],
        borderWidth: 2,
        borderColor: '#fff',
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
    },
  });

  state.chartInstances.bar = new Chart(document.getElementById('chart-bar'), {
    type: 'bar',
    data: {
      labels: ['Audio Score', 'Behavioral Score', 'Fusion Score'],
      datasets: [{
        label: 'Latest Analysis',
        data: [0, 0, 0],
        backgroundColor: ['#89c4f4', '#f0c040', '#2d5a3d'],
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { min: 0, max: 1, grid: { color: '#f0ede8' } },
        x: { grid: { display: false } },
      },
    },
  });

  updateCharts();
}

function updateCharts() {
  if (!state.chartsInit) return;

  const latest = state.fusionResults.length ? state.fusionResults[state.fusionResults.length - 1] : { audio: 0, beh: 0, fusion: 0 };

  // Pie chart: Class Probability based on latest fusion score
  const riskProb = latest.fusion || 0;
  const healthyProb = 1 - riskProb;

  if (state.chartInstances.pie) {
    state.chartInstances.pie.data.datasets[0].data = [healthyProb, riskProb];
    state.chartInstances.pie.update();
  }

  if (state.chartInstances.bar) {
    state.chartInstances.bar.data.datasets[0].data = [latest.audio || 0, latest.beh || 0, latest.fusion || 0];
    state.chartInstances.bar.update();
  }
}

