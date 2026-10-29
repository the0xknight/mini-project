import * as ort from 'onnxruntime-web';
import { extractFeaturesFromUrl } from './featureExtractor.js';

// Explicitly lock down the WASM configuration to prevent threaded / JSEP imports
ort.env.wasm.wasmPaths = chrome.runtime.getURL('wasm/');
ort.env.wasm.numThreads = 1;
ort.env.wasm.proxy = false;

// Force single-threaded SIMD backend directly
ort.env.wasm.simd = true;

let session = null;

async function loadModel() {
  if (session) return session;
  try {
    const modelUrl = chrome.runtime.getURL('assets/model.onnx');
    const response = await fetch(modelUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch model: ${response.statusText}`);
    }
    const buffer = await response.arrayBuffer();

    session = await ort.InferenceSession.create(buffer, {
      executionProviders: ['wasm']
    });
    console.log('[EdgePhish Offscreen] ONNX WASM Engine Loaded and Ready!');
    return session;
  } catch (err) {
    console.error('[EdgePhish Offscreen] Failed to load ONNX model:', err);
    throw err;
  }
}

// Pre-load on startup
loadModel().catch(console.error);

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'SCAN_URL') {
    handleScan(message.url)
      .then(result => sendResponse(result))
      .catch(err => sendResponse({ error: err.message }));
    return true; // Keep channel open for async response
  }
});

async function handleScan(url) {
  if (!session) {
    await loadModel();
  }

  const startTime = performance.now();
  const features = extractFeaturesFromUrl(url);
  const tensor = new ort.Tensor('float32', features, [1, 16]);

  const inputName = session.inputNames[0];
  const results = await session.run({ [inputName]: tensor });
  const elapsed = (performance.now() - startTime).toFixed(2);

  const probTensor = results.probabilities || results[session.outputNames[1]];
  const phishProbability = probTensor.data[1];

  return {
    url: url,
    phishProbability: phishProbability,
    isPhishing: phishProbability > 0.70,
    latencyMs: elapsed
  };
}
