import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import m2cgen as m2c

# 1. Load data
df = pd.read_csv(os.path.join("data", "dataset.csv"))
X = df.drop(columns=['label'])
y = df['label']

X_train, _, y_train, _ = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

# 2. Train model (n_estimators=50, max_depth=8 for speed and compact size)
clf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

# 3. Transpile directly into a JavaScript function
print("Transpiling Random Forest to JavaScript...")
js_code = m2c.export_to_javascript(clf)

# Wrap in an ES Module export without variable shadowing
module_code = f"""// Auto-generated pure JS decision tree model
{js_code}

export function predictPhishing(inputVector) {{
  const rawScore = score(inputVector);
  if (Array.isArray(rawScore)) {{
    return rawScore[1];
  }}
  return rawScore;
}}
"""

with open("model.js", "w") as f:
    f.write(module_code)

print("[SUCCESS] Exported pure JS model to model.js!")