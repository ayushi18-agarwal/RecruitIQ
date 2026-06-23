# 🚀 RecruitIQ

### AI-Powered Recruitment Intelligence & Decision Support Platform

RecruitIQ is an AI-powered Recruitment Intelligence and Decision Support Platform designed to optimize the entire talent acquisition lifecycle. The platform combines semantic candidate evaluation, recruitment analytics, interview intelligence, workflow automation, and AI-assisted decision support to help organizations make faster and more informed hiring decisions.

Unlike traditional Applicant Tracking Systems (ATS) that primarily focus on application tracking and keyword filtering, RecruitIQ leverages Artificial Intelligence, Natural Language Processing (NLP), Semantic Similarity Analysis, and Large Language Models (LLMs) to automate candidate evaluation, skill-gap detection, interview preparation, recruiter insights, and hiring workflows.

---

# 🎯 Project Objective

Modern organizations receive hundreds of applications for a single position, making manual resume screening time-consuming and inconsistent.

RecruitIQ addresses this challenge by:

✅ Automating candidate screening and ranking

✅ Performing semantic candidate-job matching

✅ Identifying strengths and skill gaps

✅ Generating ATS fit scores and hiring recommendations

✅ Providing AI-powered interview preparation

✅ Delivering recruitment analytics and insights

✅ Supporting recruiters through intelligent decision-making tools

---

# 🌟 Why RecruitIQ?

Unlike conventional ATS platforms that focus primarily on storing applications and keyword filtering, RecruitIQ functions as a Recruitment Intelligence Platform.

The system combines:

* Semantic Talent Intelligence
* AI Candidate Evaluation
* Skill Gap Analysis
* Recruitment Analytics
* Interview Intelligence
* Voice-Enabled HR Assistance
* Automated Recruiter Notifications

into a unified ecosystem.

RecruitIQ assists recruiters not only in managing applications but also in making faster, smarter, and more data-driven hiring decisions.

---

# ✨ Key Features

## 🧠 Semantic Talent Intelligence Engine

* Upload resumes in PDF and DOCX formats
* Automated resume parsing and candidate information extraction
* MiniLM-based semantic understanding
* Job-description aware candidate evaluation
* Experience validation and profile analysis

---

## 📊 Recruitment Decision Engine

* ATS fit score generation
* Candidate-job compatibility analysis
* Hiring recommendation generation
* Strong Hire / Hire / Review / Reject classification
* Recruiter-facing decision support

---

## 🤖 AI-Powered Candidate Evaluation

Uses:

* MiniLM Sentence Transformer
* Cosine Similarity Analysis
* LLaMA 3.3 70B (Groq API)

Generates:

* Match Scores
* Candidate Summaries
* Skill Analysis
* Missing Skills Reports
* Hiring Insights

---

## 🏆 Candidate Ranking System

Automatically ranks applicants based on:

* Semantic Relevance
* Skill Coverage
* Experience Match
* ATS Score
* Job Fit

---

## 📈 Recruitment Intelligence Dashboard

Provides:

* Real-time hiring analytics
* Candidate pipeline monitoring
* Application statistics
* Skill-gap intelligence
* Hiring trend visualization
* Interactive charts using Chart.js

---

## 🎤 Voice-Enabled HR Assistant

* Natural language interaction
* Voice-based recruiter queries
* Candidate search through voice commands
* HR workflow automation

---

## 📝 Interview Intelligence Layer

Powered by LLaMA 3.3 70B

Generates:

* Personalized interview questions
* Skill-gap focused assessments
* Technical interview questions
* Behavioral interview questions
* Candidate evaluation guidance

---

## 📧 Automated Recruiter Alerts

* Strong Hire detection
* Email notifications for high-potential candidates
* Faster recruiter response
* Automated candidate prioritization

---

## 🔐 Secure Authentication

* Firebase Authentication
* Google OAuth Integration
* Role-Based Access Control
* Session Management

---

## 🛡 Security Features

* File extension validation
* MIME type verification
* Binary content inspection
* Secure upload handling
* Session protection mechanisms
* Sandboxed storage architecture

---

# 🛠 Technology Stack

## Backend

* Python
* Flask

## Database

* SQLite

## Artificial Intelligence & NLP

* MiniLM (all-MiniLM-L6-v2)
* Sentence Transformers
* Cosine Similarity
* LLaMA 3.3 70B (Groq API)

## Resume Processing

* PyMuPDF
* PDFPlumber
* Python-Docx

## Security

* Google Magika
* Secure File Validation
* Session Protection

## Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

## Authentication

* Firebase Authentication
* Google OAuth 2.0

## Voice Assistant

* Web Speech API

## Integration

* Zapier
* LinkedIn Job Syndication

## Version Control

* Git
* GitHub

---

# 📂 Project Structure

```text
RecruitIQ/
│
├── app.py
├── utils.py
├── train_models.py
├── test_pipeline.py
├── requirements.txt
├── .env
│
├── model.pkl
├── vectorizer.pkl
├── resume_data.csv
├── smart_hire.db
│
├── uploads/
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── app.js
│       └── voice_assistant.js
│
├── templates/
│   ├── base.html
│   ├── welcome.html
│   ├── login.html
│   ├── dashboard.html
│   ├── jobs.html
│   ├── candidates.html
│   ├── reports.html
│   ├── prep.html
│   ├── career.html
│   ├── candidate_home.html
│   └── candidate_status.html
│
├── __pycache__/
└── .dist/
```

---

# ⚙️ Installation

## Clone the Repository

```bash
git clone https://github.com/yourusername/RecruitIQ.git
cd RecruitIQ
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000
```

---

# 📊 System Workflow

```text
Candidate Application
        │
        ▼
Security Validation Layer
        │
        ▼
Document Parsing Engine
        │
        ▼
Semantic Talent Intelligence Engine
(MiniLM Embeddings)
        │
        ▼
Cosine Similarity Analysis
        │
        ▼
Skill Coverage & Experience Validation
        │
        ▼
Recruitment Decision Engine
        │
        ▼
ATS Score & Recommendation
        │
        ▼
Candidate Ranking
        │
        ▼
Database Storage
        │
        ▼
Recruitment Intelligence Dashboard
        │
        ▼
Interview Intelligence Layer
(LLaMA 3.3 70B)
        │
        ▼
Voice HR Assistant & Recruiter Alerts
```

---

# 📈 Core Modules

| Module                       | Function                                     |
| ---------------------------- | -------------------------------------------- |
| Security Layer               | Validates uploaded files                     |
| Resume Parser                | Extracts text from resumes                   |
| Semantic Intelligence Engine | Generates embeddings and evaluates relevance |
| ATS Engine                   | Calculates fit scores and recommendations    |
| Skill Gap Analyzer           | Identifies missing skills                    |
| Candidate Ranking System     | Prioritizes applicants                       |
| Recruitment Dashboard        | Visual hiring insights                       |
| Interview Intelligence       | AI-generated interview preparation           |
| Voice Assistant              | HR query automation                          |
| Authentication System        | Secure access management                     |

---

# 🎯 Sample Use Case

## Job Requirement

**Python Developer**

Required Skills:

* Python
* Flask
* Docker

### Candidate Evaluation Process

RecruitIQ automatically:

1. Extracts resume content
2. Generates semantic embeddings using MiniLM
3. Compares resume with job requirements
4. Calculates semantic similarity
5. Identifies strengths and missing skills
6. Generates ATS fit score
7. Ranks the candidate
8. Produces interview questions
9. Notifies recruiters for Strong Hire candidates

---


# 🔮 Future Roadmap

* PostgreSQL Migration for Enterprise Scalability
* LinkedIn API Integration
* Workday Integration
* AI Candidate Recommendation Engine
* Predictive Hiring Analytics
* Resume Fraud Detection
* Vector Database Integration (FAISS/Pinecone)
* Video Interview Intelligence
* AI Interview Copilot
* Multi-Tenant SaaS Deployment
* Docker & Kubernetes Deployment
* Multilingual Recruitment Support

---

# 🌍 Sustainable Development Goals (SDGs)

### SDG 8 – Decent Work and Economic Growth

Improves recruitment efficiency and helps organizations connect with suitable talent faster.

### SDG 9 – Industry, Innovation and Infrastructure

Promotes AI-driven innovation within Human Resource Management and recruitment operations.

### SDG 4 – Quality Education

Identifies skill gaps and encourages continuous learning and professional development.

---

# 💼 Business Impact

RecruitIQ significantly reduces manual recruitment effort by automating candidate evaluation and recruitment workflows.

Benefits include:

* Reduced resume screening time
* Faster hiring decisions
* Improved candidate-job matching
* Consistent evaluation standards
* Enhanced recruiter productivity
* Better talent acquisition outcomes
* Data-driven recruitment insights

---

# 👩‍💻 Author

**Ayushi Agarwal**

B.Tech Student | AI & Data Science Enthusiast

---

## ⭐ If you found this project useful, please consider giving it a star on GitHub!

---

## About

RecruitIQ is an AI-powered Recruitment Intelligence and Decision Support Platform that automates candidate evaluation, interview preparation, recruiter analytics, and hiring workflows using semantic AI and Large Language Models.
