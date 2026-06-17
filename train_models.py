import pandas as pd
import numpy as np
import pickle
import re
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.utils.class_weight import compute_class_weight
from sentence_transformers import SentenceTransformer

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

# Load and prepare data
df = pd.read_csv('resume_data.csv')
job_column = '\ufeffjob_position_name'
df['combined_text'] = (df['skills'].fillna('') + ' ' + df['career_objective'].fillna('') + ' ' + df['responsibilities'].fillna('')).apply(clean_text)
df_clean = df.dropna(subset=[job_column, 'matched_score'])
# In your Flask route where you analyze the resume:
# 1. Fetch the job from your database using the job_id
job = db.get_job_by_id(job_id) 

# 2. Pass the 'skills' field from your DB to the utility function
result = evaluate_candidate(resume_content, job.title, job.skills)
# Generate Embeddings
print("🧮 Generating embeddings...")
model = SentenceTransformer('all-MiniLM-L6-v2')
X = model.encode(df_clean['combined_text'].tolist())
y_class = df_clean[job_column].values
y_score = df_clean['matched_score'].values

# --- PERFECT SYNC SPLIT ---
indices = np.arange(len(X))
train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42)

X_train, X_test = X[train_idx], X[test_idx]
y_class_train, y_class_test = y_class[train_idx], y_class[test_idx]
y_score_train, y_score_test = y_score[train_idx], y_score[test_idx]

# Train Classifier
weights = compute_class_weight('balanced', classes=np.unique(y_class_train), y=y_class_train)
class_model = LogisticRegression(class_weight=dict(zip(np.unique(y_class_train), weights))).fit(X_train, y_class_train)

# Train Regressor
score_model = Ridge().fit(X_train, y_score_train)

# Save
with open('domain_classifier.pkl', 'wb') as f: pickle.dump(class_model, f)
with open('score_regressor.pkl', 'wb') as f: pickle.dump(score_model, f)
print("🚀 Training complete and models saved.")