const params = new URLSearchParams(window.location.search);
const targetUrl = params.get('url') || 'Unknown Target';
const score = params.get('score') || '0';
const latency = params.get('time') || '0';

document.getElementById('target-url').textContent = targetUrl;
document.getElementById('risk-score').textContent = `${(parseFloat(score) * 100).toFixed(1)}%`;
document.getElementById('inference-time').textContent = `${latency} ms`;

document.getElementById('btn-back').addEventListener('click', () => {
  window.history.length > 1 ? window.history.back() : window.close();
});

document.getElementById('btn-proceed').addEventListener('click', () => {
  // Let the user proceed by setting an ignore flag in session storage
  chrome.runtime.sendMessage({ type: 'WHITELIST_TEMPORARY', url: targetUrl }, () => {
    window.location.href = targetUrl;
  });
});