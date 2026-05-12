// NeuroScreen — tab navigation

function initTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.pane').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('pane-' + tab.dataset.tab).classList.add('active');

      if (tab.dataset.tab === 'charts') {
        initCharts();
        updateCharts();
      }
      if (tab.dataset.tab === 'fusion') updateDomainDisplay();
    });
  });
}

document.addEventListener('DOMContentLoaded', initTabs);
