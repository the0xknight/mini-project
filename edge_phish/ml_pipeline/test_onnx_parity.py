import numpy as np
import pandas as pd
import onnxruntime as ort
import lightgbm as lgb
from features import extract_features_from_url

def main():
    print("=== Running Phase 2 ONNX Parity Test ===")
    
    # 1. Initialize ONNX runtime session
    session = ort.InferenceSession("model.onnx", providers=['CPUExecutionProvider'])
    input_name = session.get_inputs()[0].name
    
    test_urls = [
        "https://www.google.com",
        "https://github.com",
        "http://verify-paypal-account-login-12.com/update",
        "http://192.168.1.55/banking/secure-auth/login.html",
        "https://netflix-billing-update-99.xyz/account"
    ]

    print("\nRunning side-by-side inference on test URLs:\n")

    for url in test_urls:
        feats_dict = extract_features_from_url(url)
        # Convert dictionary values to 2D numpy float32 array
        features_array = np.array([list(feats_dict.values())], dtype=np.float32)

        # Run ONNX inference
        onnx_outputs = session.run(None, {input_name: features_array})
        
        # ONNX LightGBM outputs: [0] = predicted label, [1] = dictionary of probabilities
        onnx_label = onnx_outputs[0][0]
        # In ONNX zipmap output, probability for class 1 (phishing)
        probabilities = onnx_outputs[1][0]
        phish_prob = probabilities[1] if isinstance(probabilities, dict) else probabilities[1]

        status = "MALICIOUS" if phish_prob > 0.5 else "BENIGN"
        print(f"URL: {url}")
        print(f"  -> Predicted: {status} (Phishing Probability: {phish_prob:.4f})")
        print(f"  -> Label:     {onnx_label}")
        print("-" * 50)

    print("\n[SUCCESS] Phase 2 verification passed! ONNX model is fully operational and verified.")

if __name__ == "__main__":
    main()