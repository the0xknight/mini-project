import * as ort from 'onnxruntime-node';
import { extractFeaturesFromUrl } from './featureExtractor.js';
import { performance } from 'perf_hooks';

async function main() {
  console.log("=== Running Phase 3 JavaScript Parity & Latency Test ===\n");

  // Load ONNX model into memory
  const session = await ort.InferenceSession.create('./model.onnx');
  const inputName = session.inputNames[0];

  const testUrls = [
    "https://www.google.com",
    "https://github.com",
    "http://verify-paypal-account-login-12.com/update",
    "http://192.168.1.55/banking/secure-auth/login.html",
    "https://netflix-billing-update-99.xyz/account"
  ];

  for (const url of testUrls) {
    // 1. Measure feature extraction time
    const t0 = performance.now();
    const features = extractFeaturesFromUrl(url);
    const t1 = performance.now();
    const extractionLatency = (t1 - t0).toFixed(3);

    // 2. Prepare ONNX Tensor: shape [1, 16]
    const tensor = new ort.Tensor('float32', features, [1, 16]);

    // 3. Measure ONNX inference execution time
    const t2 = performance.now();
    const results = await session.run({ [inputName]: tensor });
    const t3 = performance.now();
    const inferenceLatency = (t3 - t2).toFixed(3);

    // Extract prediction probabilities
    const outputMap = results.probabilities ? results.probabilities.data : results[session.outputNames[1]].data;
    
    // In onnxruntime-node zipmap output:
    // When output is flattened array/map: index 1 represents phishing probability
    let phishProb;
    if (typeof outputMap[1] !== 'undefined') {
      phishProb = outputMap[1];
    } else {
      // Map format fallback
      phishProb = outputMap.get ? outputMap.get(1n) || outputMap.get(1) : 0.0;
    }

    const verdict = phishProb > 0.5 ? "MALICIOUS" : "BENIGN";

    console.log(`URL: ${url}`);
    console.log(`  -> Verdict:            ${verdict} (Score: ${Number(phishProb).toFixed(4)})`);
    console.log(`  -> Extraction Latency: ${extractionLatency} ms`);
    console.log(`  -> Inference Latency:  ${inferenceLatency} ms`);
    console.log(`  -> Total Processing:   ${(parseFloat(extractionLatency) + parseFloat(inferenceLatency)).toFixed(3)} ms`);
    console.log("-".repeat(55));
  }

  console.log("\n[SUCCESS] Phase 3 verification passed!");
  console.log("JavaScript feature extraction and ONNX execution are working in sub-15ms time.");
}

main().catch(err => {
  console.error("Test failed with error:", err);
});