"""
train_models.py — SmartHire ML Training Pipeline
=================================================
Reads:  merged_training_data.csv  (9,846 rows, 34 domains)
        — pre-merged from resume_data.csv + CareerCorpus.xlsx

Produces:
  score_regressor.pkl    — Ridge regression  → fit score 0-100
  domain_classifier.pkl  — Logistic Regression → job domain label
  label_encoder.pkl      — decodes domain numbers back to names

Run once from project root:
    python train_models.py
"""

import os, re, pickle, warnings
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.metrics import mean_absolute_error
from sklearn.utils.class_weight import compute_class_weight
from sklearn.preprocessing import LabelEncoder
from sentence_transformers import SentenceTransformer

warnings.filterwarnings('ignore')

DATA_FILE = 'merged_training_data.csv'   # place in same folder as app.py

# ── 1. LOAD ───────────────────────────────────────────────────────────────────

def load_data(path=DATA_FILE):
    print(f"Loading {path} ...")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Place it in the same folder as train_models.py."
        )
    df = pd.read_csv(path)
    df = df.dropna(subset=['combined_text', 'domain', 'score_100'])
    df = df[df['combined_text'].str.strip().str.len() > 30].copy()
    print(f"  {len(df)} rows | {df['domain'].nunique()} domains | "
          f"score {df['score_100'].min():.0f}-{df['score_100'].max():.0f}")
    print(f"  Sources: {df['source'].value_counts().to_dict()}")
    return df

# ── 2. EMBED ──────────────────────────────────────────────────────────────────

def generate_embeddings(texts):
    print(f"\nGenerating embeddings ({len(texts)} rows) — ~2-4 min on CPU ...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    X = embedder.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
    print(f"  Done: {X.shape}")
    return X

# ── 3. TRAIN REGRESSOR ────────────────────────────────────────────────────────

def train_regressor(X, y):
    print("\nTraining score regressor (Ridge, 5-fold CV) ...")
    maes = []
    for fold, (tr, val) in enumerate(KFold(n_splits=5, shuffle=True, random_state=42).split(X), 1):
        m = Ridge(alpha=1.0)
        m.fit(X[tr], y[tr])
        preds = np.clip(m.predict(X[val]), 0, 100)
        mae = mean_absolute_error(y[val], preds)
        maes.append(mae)
        print(f"  Fold {fold}: MAE = {mae:.1f} pts")
    print(f"  Mean MAE: {np.mean(maes):.1f} +/- {np.std(maes):.1f} pts (0-100 scale)")
    final = Ridge(alpha=1.0)
    final.fit(X, y)
    return final

# ── 4. TRAIN CLASSIFIER ───────────────────────────────────────────────────────

def train_classifier(X, y_labels):
    print("\nTraining domain classifier (Logistic Regression, 5-fold CV) ...")
    le = LabelEncoder()
    y_enc = le.fit_transform(y_labels)
    base = LogisticRegression(class_weight='balanced', max_iter=1000, C=1.0, solver='lbfgs')
    accs = cross_val_score(base, X, y_enc,
                           cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
                           scoring='accuracy')
    for i, a in enumerate(accs, 1):
        print(f"  Fold {i}: Accuracy = {a*100:.1f}%")
    print(f"  Mean Accuracy: {accs.mean()*100:.1f}% +/- {accs.std()*100:.1f}%")
    cw = compute_class_weight('balanced', classes=np.unique(y_enc), y=y_enc)
    final = LogisticRegression(
        class_weight=dict(zip(np.unique(y_enc), cw)),
        max_iter=1000, C=1.0, solver='lbfgs'
    )
    final.fit(X, y_enc)
    return final, le

# ── 5. SAVE ───────────────────────────────────────────────────────────────────

def save_model(obj, filename):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
    print(f"  Saved {filename} ({os.path.getsize(filename)/1024:.0f} KB)")

# ── 6. MAIN ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 55)
    print("  SmartHire — ML Training Pipeline")
    print("=" * 55)

    df         = load_data()
    X          = generate_embeddings(df['combined_text'].tolist())
    regressor              = train_regressor(X, df['score_100'].values)
    classifier, label_enc  = train_classifier(X, df['domain'].values)

    print("\nSaving models ...")
    save_model(regressor,  'score_regressor.pkl')
    save_model(classifier, 'domain_classifier.pkl')
    save_model(label_enc,  'label_encoder.pkl')

    print("\n" + "=" * 55)
    print("  Done! 3 files saved:")
    print("    score_regressor.pkl")
    print("    domain_classifier.pkl")
    print("    label_encoder.pkl")
    print("  Restart app.py — models load automatically.")
    print("=" * 55)