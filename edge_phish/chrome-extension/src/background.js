import { extractFeaturesFromUrl } from './featureExtractor.js';
import { predictPhishing } from './model.js';

const tempWhitelist = new Set();

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'WHITELIST_TEMPORARY') {
    tempWhitelist.add(message.url);
    sendResponse({ success: true });
  }
});

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (details.frameId !== 0) return;

  const url = details.url;
  if (!url || url.startsWith('chrome://') || url.startsWith('chrome-extension://')) {
    return;
  }

  // Allow navigation if the user clicked "Proceed Anyway"
  if (tempWhitelist.has(url)) {
    tempWhitelist.delete(url);
    return;
  }

  const startTime = performance.now();
  const features = extractFeaturesFromUrl(url);
  const score = predictPhishing(Array.from(features));
  const latency = (performance.now() - startTime).toFixed(2);

  console.log(`[EdgePhish] Scanned: ${url} | Score: ${score} | Time: ${latency}ms`);

  // Block navigation when risk score is greater than 60%
  if (score > 0.60) {
    const warningUrl = chrome.runtime.getURL(
      `warning.html?url=${encodeURIComponent(url)}&score=${score}&time=${latency}`
    );
    chrome.tabs.update(details.tabId, { url: warningUrl });
  }
});