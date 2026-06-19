"""
utils.py — SmartHire Core Utilities
=====================================
Scoring pipeline:
  35% Semantic similarity  (frozen all-MiniLM-L6-v2)
  35% Skill keyword match  (alias-aware)
  30% Ridge regressor      (trained on 9,544 + 302 labelled resumes)
  +   Experience bonus     (up to +10 pts)

New feature:
  get_resume_critique()  — Groq LLM 2-3 sentence qualitative critique
"""

import os, re, pickle
import numpy as np
import fitz                          # PyMuPDF for PDF reading
import spacy
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── NLP + Embedding model (frozen, never retrained) ───────────────────────────
nlp      = spacy.load("en_core_web_sm")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# ── Load trained ML models ────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))

def _load(fname):
    path = os.path.join(_DIR, fname)
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"WARNING: could not load {fname}: {e}")
    return None

score_regressor   = _load('score_regressor.pkl')
domain_classifier = _load('domain_classifier.pkl')
label_encoder     = _load('label_encoder.pkl')

if score_regressor:
    print("ML models loaded (score_regressor + domain_classifier)")
else:
    print("WARNING: ML models not found — run train_models.py. Falling back to rule-based scoring.")

# ── Groq client ───────────────────────────────────────────────────────────────
_groq_key = os.getenv("GROQ_API_KEY")
if not _groq_key:
    raise EnvironmentError("GROQ_API_KEY is not set. Add it to your .env file.")

client = OpenAI(api_key=_groq_key, base_url="https://api.groq.com/openai/v1")


# ═══════════════════════════════════════════════════════════════════════════════
#  TEXT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', ' ', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text(file_path):
    text = ""
    if file_path.endswith('.pdf'):
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    else:
        with open(file_path, 'r', errors='ignore') as f:
            text = f.read()
    return text


# ═══════════════════════════════════════════════════════════════════════════════
#  SKILL UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

SKILL_ALIASES = {
    'ml': 'machine learning', 'machine learning': 'ml',
    'dl': 'deep learning',    'deep learning': 'dl',
    'nlp': 'natural language processing', 'natural language processing': 'nlp',
    'ai': 'artificial intelligence',      'artificial intelligence': 'ai',
    'js': 'javascript', 'javascript': 'js',
    'ts': 'typescript', 'typescript': 'ts',
    'k8s': 'kubernetes', 'kubernetes': 'k8s',
    'tf': 'tensorflow', 'tensorflow': 'tf',
    'db': 'database',   'database': 'db',
    'oop': 'object oriented programming',
    'ci/cd': 'continuous integration', 'cicd': 'continuous integration',
    'aws': 'amazon web services', 'amazon web services': 'aws',
    'gcp': 'google cloud platform',  'google cloud platform': 'gcp',
    'postgres': 'postgresql', 'postgresql': 'postgres',
    'mongo': 'mongodb',       'mongodb': 'mongo',
    'react.js': 'react', 'reactjs': 'react',
    'node.js': 'nodejs', 'node': 'nodejs',
    'vue.js': 'vue',     'vuejs': 'vue',
    'next.js': 'nextjs',
    'c++': 'cpp',  'cpp': 'c++',
    'rest api': 'rest', 'restful': 'rest',
}

def skill_matches(required_skill, resume_lower):
    if required_skill in resume_lower:
        return True
    alias = SKILL_ALIASES.get(required_skill)
    return bool(alias and alias in resume_lower)

def extract_skills(text):
    doc = nlp(text.lower())
    return {t.text for t in doc if t.pos_ in ['NOUN', 'PROPN'] and len(t.text) > 2}


# ═══════════════════════════════════════════════════════════════════════════════
#  EXPERIENCE PARSING
# ═══════════════════════════════════════════════════════════════════════════════

def extract_experience_years(resume_text):
    text = resume_text.lower()
    patterns = [
        r'(\d{1,2})\+?\s*(?:years|yrs|year)\s*(?:of)?\s*experience',
        r'experience\s*(?:of)?\s*(\d{1,2})\+?\s*(?:years|yrs|year)',
        r'(\d{1,2})\+?\s*(?:years|yrs)\s*in\b',
    ]
    found = []
    for pat in patterns:
        for m in re.findall(pat, text):
            try:
                y = int(m)
                if 0 < y <= 40:
                    found.append(y)
            except (ValueError, TypeError):
                pass
    return max(found) if found else 0

def extract_required_experience(exp_str):
    if not exp_str: return 0
    m = re.search(r'(\d{1,2})', str(exp_str))
    return int(m.group(1)) if m else 0


# ═══════════════════════════════════════════════════════════════════════════════
#  ATS LABEL
# ═══════════════════════════════════════════════════════════════════════════════

def get_ats_recommendation(score):
    if score >= 75: return 'Strong Hire'
    if score >= 55: return 'Hire'
    return 'Review'


# ═══════════════════════════════════════════════════════════════════════════════
#  GROQ — INTERVIEW QUESTIONS  (existing feature, unchanged)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_interview_questions(candidate_name, job_title, job_description,
                                  job_skills, skills_found, skills_missing,
                                  resume_text=""):
    resume_snippet = resume_text.strip()[:3000] if resume_text else "Not provided"
    prompt = f"""
You are a senior technical interviewer at a top tech company generating a personalized interview guide.

CANDIDATE NAME: {candidate_name}
ROLE: {job_title}
JOB DESCRIPTION: {job_description}
REQUIRED SKILLS: {job_skills}
VERIFIED SKILLS (found in resume): {skills_found if skills_found else "Not detected"}
SKILL GAPS (required but missing): {skills_missing if skills_missing else "None"}

CANDIDATE RESUME:
---
{resume_snippet}
---

Generate exactly 5 interview questions. Return ONLY a JSON array, no markdown, no explanation.
Each object must have these exact keys: "type", "title", "question", "tip"

Rules:
- Q1: type="Deep Technical" — Reference a SPECIFIC tool or project from their resume.
- Q2: type="Deep Technical" — Pick one verified skill and ask a hard scenario.
- Q3: type="Skill Gap Probe" — Target a skill gap. Be diagnostic.
- Q4: type="Skill Gap Probe" — Another gap in a realistic production scenario.
- Q5: type="Behavioral" — Probe ownership, problem-solving, or collaboration under pressure.

STRICT RULES:
- Every question must be specific to THIS candidate's resume.
- Never ask generic questions.
- The "tip" must explain what a STRONG vs WEAK answer looks like.
- Return ONLY the JSON array. No other text.

Example format:
[{{"type":"Deep Technical","title":"Flask + SQLAlchemy","question":"...","tip":"Strong: ... Weak: ..."}}]
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You return ONLY valid JSON arrays. No markdown, no preamble."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.9,
        max_tokens=2000,
    )
    return response.choices[0].message.content


# ═══════════════════════════════════════════════════════════════════════════════
#  GROQ — RESUME CRITIQUE  (NEW feature)
# ═══════════════════════════════════════════════════════════════════════════════

def get_resume_critique(candidate_name, job_title, fit_score,
                         skills_found, skills_missing, resume_text=""):
    """
    Returns a 2-3 sentence qualitative critique of the resume.
    Adds nuance the numeric score alone cannot capture.
    Called after evaluate_candidate() — adds ~1-2s latency (Groq is fast).
    """
    resume_snippet = resume_text.strip()[:2000] if resume_text else "Not provided"

    prompt = f"""
You are a senior HR analyst reviewing a candidate's resume for a job application.

CANDIDATE: {candidate_name}
ROLE APPLIED: {job_title}
AI FIT SCORE: {fit_score}/100
SKILLS MATCHED: {skills_found if skills_found else "None detected"}
SKILL GAPS: {skills_missing if skills_missing else "None"}

RESUME EXCERPT:
---
{resume_snippet}
---

Write EXACTLY 2-3 sentences of qualitative critique. Be specific, honest, and professional.
Cover: (1) their strongest qualification for this role, (2) the biggest concern or gap, 
and (3) one concrete suggestion to improve their application.

Return ONLY the critique text. No bullet points, no headers, no JSON. Just plain sentences.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional HR analyst. Write concise, specific, honest resume critiques in plain prose."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.6,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Critique generation error: {e}")
        return ""


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN SCORING FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_candidate(resume_text, job_title, job_description,
                        required_skills_str, job_experience=""):
    """
    Blended scoring:
      35% Semantic similarity   (cosine sim via MiniLM — always runs)
      35% Skill keyword match   (alias-aware — always runs)
      30% Ridge regressor score (ML model trained on labelled dataset)
      +   Experience bonus      (0, +4, or +10 pts)

    Falls back to 45/45 semantic/skill split if ML models aren't loaded.
    """
    resume_lower = resume_text.lower()

    # ── 1. Semantic similarity ─────────────────────────────────────────────────
    res_emb  = embedder.encode(resume_text,    convert_to_tensor=True)
    job_emb  = embedder.encode(job_description, convert_to_tensor=True)
    cos_raw  = util.cos_sim(res_emb, job_emb).item()          # -1.0 to 1.0
    semantic = int(((cos_raw + 1) / 2) * 100)                 # → 0-100
    semantic = max(0, min(100, semantic))

    # ── 2. Skill keyword match ─────────────────────────────────────────────────
    required = {s.strip().lower() for s in required_skills_str.split(',') if s.strip()}
    found    = {sk for sk in required if skill_matches(sk, resume_lower)}
    missing  = required - found
    skill_cov = int((len(found) / len(required)) * 100) if required else 0
    skill_cov = max(0, min(100, skill_cov))

    # ── 3. ML regressor ────────────────────────────────────────────────────────
    ml_score = None
    if score_regressor is not None:
        try:
            combined = clean_text(
                resume_text + " " + job_title + " " + job_description + " " + required_skills_str
            )
            vec      = embedder.encode([combined], convert_to_numpy=True)
            ml_score = float(np.clip(score_regressor.predict(vec)[0], 0, 100))
        except Exception as e:
            print(f"ML regressor error: {e}")

    # ── 4. Domain prediction (informational — not in score blend) ──────────────
    predicted_domain = None
    if domain_classifier is not None and label_encoder is not None:
        try:
            vec = embedder.encode([clean_text(resume_text)], convert_to_numpy=True)
            enc = domain_classifier.predict(vec)[0]
            predicted_domain = label_encoder.inverse_transform([enc])[0]
        except Exception as e:
            print(f"Domain classifier error: {e}")

    # ── 5. Experience bonus ────────────────────────────────────────────────────
    cand_yrs = extract_experience_years(resume_text)
    req_yrs  = extract_required_experience(job_experience)
    exp_bonus = 0
    exp_note  = "Not detected"

    if cand_yrs > 0:
        if req_yrs == 0:
            exp_bonus = 3
            exp_note  = f"{cand_yrs} yrs found (no minimum specified)"
        elif cand_yrs >= req_yrs:
            exp_bonus = 10
            exp_note  = f"{cand_yrs} yrs meets/exceeds {req_yrs} yr requirement"
        elif cand_yrs >= req_yrs * 0.6:
            exp_bonus = 4
            exp_note  = f"{cand_yrs} yrs is slightly below {req_yrs} yr requirement"
        else:
            exp_bonus = 0
            exp_note  = f"{cand_yrs} yrs is well below {req_yrs} yr requirement"

    # ── 6. Blend ───────────────────────────────────────────────────────────────
    if ml_score is not None:
        # Full blend: 35% semantic + 35% skill + 30% ML
        raw = int(semantic * 0.35 + skill_cov * 0.35 + ml_score * 0.30) + exp_bonus
    else:
        # Fallback: 45% semantic + 45% skill (no ML)
        raw = int(semantic * 0.45 + skill_cov * 0.45) + exp_bonus

    final_score = max(0, min(100, raw))

    return {
        'fit_score':      final_score,
        'recommendation': get_ats_recommendation(final_score),
        'skills_found':   ", ".join(sorted(found))   if found   else "",
        'skills_missing': ", ".join(sorted(missing)) if missing else "",
        'breakdown': {
            'semantic_score':   semantic,
            'skill_coverage':   skill_cov,
            'ml_score':         round(ml_score, 1) if ml_score is not None else "N/A",
            'ml_model_used':    ml_score is not None,
            'predicted_domain': predicted_domain or "N/A",
            'experience_bonus': exp_bonus,
            'experience_note':  exp_note,
            'candidate_years':  cand_yrs,
            'required_years':   req_yrs,
        }
    }