import os
import re
import fitz
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer, util

# Load models once
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text(file_path):
    text = ""
    if file_path.endswith('.pdf'):
        with fitz.open(file_path) as doc:
            for page in doc: text += page.get_text()
    else:
        with open(file_path, 'r', errors='ignore') as f:
            text = f.read()
    return text

def generate_interview_questions(candidate_name, job_title, skills_found, skills_missing):
    # This remains as your foundation; you can pipe this into your AI later
    return f"Interview guide for {candidate_name} targeting {job_title}. Skills found: {skills_found}. Focus on: {skills_missing}"

def get_ats_recommendation(score):
    if score >= 75: return 'Strong Hire'
    if score >= 55: return 'Hire'
    return 'Review'

def extract_skills(text):
    doc = nlp(text.lower())
    return {token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2}

def evaluate_candidate(resume_text, job_title, job_description, required_skills_str):
    # 1. Semantic fit (Keeping your existing logic)
    res_emb = embedder.encode(resume_text, convert_to_tensor=True)
    job_emb = embedder.encode(job_description, convert_to_tensor=True)
    semantic_score = int(util.cos_sim(res_emb, job_emb).item() * 100)
    
    # 2. IMPROVED Skill Match: Direct Keyword Check
    required = {s.strip().lower() for s in required_skills_str.split(',')}
    cleaned_resume = resume_text.lower()
    
    # Find skills by checking if the required word exists anywhere in the text
    found = {skill for skill in required if skill in cleaned_resume}
    missing = required - found
    
    # 3. Calculate Scores
    skill_coverage = int((len(found) / len(required)) * 100) if required else 0
    final_score = int((semantic_score * 0.5) + (skill_coverage * 0.5))
    
    # 4. Return clean strings (Use empty string instead of "None" for easier UI handling)
    return {
        'fit_score': final_score,
        'recommendation': get_ats_recommendation(final_score),
        'skills_found': ", ".join(found) if found else "",
        'skills_missing': ", ".join(missing) if missing else ""
    }