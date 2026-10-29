import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, confusion_matrix, roc_auc_score
)
from skl2onnx import to_onnx
import onnx

def main():
    dataset_path = os.path.join("data", "dataset.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Missing {dataset_path}. Run build_dataset.py first!")

    print("[1/4] Loading and splitting dataset...")
    df = pd.read_csv(dataset_path)

    X = df.drop(columns=['label'])
    y = df['label']
    feature_names = list(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Features: {len(feature_names)} | Training: {X_train.shape[0]} | Testing: {X_test.shape[0]}")

    print("[2/4] Training Random Forest Classifier...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    print("[3/4] Evaluating Model Performance...")
    y_pred = clf.predict(X_test)
    y_probs = clf.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_probs)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    fpr = fp / (fp + tn)

    print("\n" + "="*45)
    print("        RESEARCH EVALUATION METRICS        ")
    print("="*45)
    print(f"Accuracy:            {acc * 100:.2f}%")
    print(f"Precision:           {prec * 100:.2f}%")
    print(f"Recall:              {rec * 100:.2f}%")
    print(f"F1-Score:            {f1:.4f}")
    print(f"AUC-ROC:             {auc:.4f}")
    print(f"False Positive Rate: {fpr * 100:.2f}%")
    print("="*45 + "\n")

    print("[4/4] Exporting to ONNX with pure tensor output (ZipMap disabled)...")
    dummy_input = X_train.iloc[:1].to_numpy(dtype=np.float32)

    # Disable zipmap directly so ONNX produces raw float32 tensors
    onnx_model = to_onnx(
        clf,
        dummy_input,
        target_opset=12,
        options={id(clf): {'zipmap': False}}
    )

    output_onnx_path = "model.onnx"
    onnx.save_model(onnx_model, output_onnx_path)

    file_size_kb = os.path.getsize(output_onnx_path) / 1024
    print(f"[SUCCESS] Exported to {output_onnx_path} ({file_size_kb:.2f} KB, clean float tensor)")

if __name__ == "__main__":
    main()