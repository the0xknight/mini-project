import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

def evaluate():
    dataset_path = os.path.join("data", "dataset.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Missing {dataset_path}")

    df = pd.read_csv(dataset_path)
    X = df.drop(columns=['label'])
    y = df['label']

    # 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    # Predictions and probabilities
    y_pred = clf.predict(X_test)
    y_probs = clf.predict_proba(X_test)[:, 1]

    # Metric calculations
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_probs)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    fpr = fp / (fp + tn)  # False Positive Rate: benign sites incorrectly blocked

    print("=" * 50)
    print("           MODEL EVALUATION BENCHMARK")
    print("=" * 50)
    print(f"Total Test URLs:         {len(y_test)}")
    print(f"Accuracy:                {acc * 100:.2f}%")
    print(f"Precision:               {prec * 100:.2f}%  (When flagged, how often is it actually phishing)")
    print(f"Recall (Detection Rate): {rec * 100:.2f}%  (Percentage of all phishing attacks caught)")
    print(f"F1-Score:                {f1:.4f}")
    print(f"AUC-ROC:                 {auc:.4f}")
    print(f"False Positive Rate:     {fpr * 100:.2f}%  (Legitimate sites wrongly flagged)")
    print("=" * 50)
    print("\nConfusion Matrix:")
    print(f"  True Negatives (Allowed Safe):     {tn}")
    print(f"  False Positives (Blocked Safe):    {fp}")
    print(f"  False Negatives (Missed Phishing): {fn}")
    print(f"  True Positives (Blocked Phishing): {tp}\n")
    print("Detailed Classification Report:\n")
    print(classification_report(y_test, y_pred, target_names=["Benign", "Phishing"]))

if __name__ == "__main__":
    evaluate()