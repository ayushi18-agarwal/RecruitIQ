# 🚀 RecruitIQ

## AI-Powered Recruitment Operations Command Center

RecruitIQ is a full-stack recruitment automation platform designed to streamline the hiring process from candidate application to interview preparation. The platform leverages Artificial Intelligence, Machine Learning, and Large Language Models (LLMs) to automate resume screening, candidate ranking, ATS scoring, skill-gap analysis, and recruitment analytics.

Built with Flask and integrated with modern AI technologies, SmartHire AI helps recruiters make faster and more data-driven hiring decisions.

---

## 🎯 Project Objective

Traditional recruitment involves manually reviewing hundreds of resumes, resulting in significant time consumption and inconsistent evaluations.

SmartHire AI addresses this challenge by:

* Automating resume screening
* Generating ATS compatibility scores
* Ranking candidates based on job requirements
* Identifying skill gaps
* Providing interview preparation assistance
* Delivering actionable hiring analytics

---

## ✨ Key Features

### 🔍 Resume Analyzer

* Upload resumes in PDF and DOCX formats.
* Extracts candidate information automatically.
* Performs text preprocessing and skill extraction.

### 📊 ATS Score Generator

* Calculates candidate-job compatibility scores.
* Evaluates resumes against job descriptions.
* Highlights strengths and weaknesses.

### 🤖 AI-Powered Candidate Evaluation

* Uses LLM integration (OpenAI/Groq).
* Generates:

  * Match Scores
  * Candidate Summaries
  * Skill Analysis
  * Missing Skills Reports

### 🏆 Candidate Ranking System

* Automatically ranks applicants based on:

  * Skills Match
  * ATS Score
  * Resume Relevance
  * Job Fit

### 📈 Recruitment Dashboard

* Real-time recruitment insights.
* Candidate analytics.
* Job application statistics.
* Interactive visualizations using Chart.js.

### 🎤 Voice-Enabled HR Assistant

* Natural language interaction.
* Candidate search through voice commands.
* HR query automation.

### 📝 Interview Preparation Generator

* Generates job-specific interview questions.
* Creates technical and behavioral question sets.
* Helps recruiters conduct structured interviews.

### 🔐 Secure Authentication

* Firebase Authentication
* Google OAuth Integration
* Role-Based Access Control

### 🛡 Security Features

* File type validation
* MIME type verification
* Secure upload handling
* Session protection mechanisms

---

## 🛠 Technology Stack

### Backend

* Python
* Flask

### Database

* SQLite

### Machine Learning

* Scikit-Learn
* TF-IDF Vectorization
* Candidate Classification Models

### Artificial Intelligence

* OpenAI API
* Groq API

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

### Authentication

* Firebase Authentication
* Google OAuth 2.0

### Resume Processing

* PDFPlumber
* Python-Docx

---

## 📂 Project Structure

```text
SmartHire/
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

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/SmartHire.git
cd SmartHire
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Mac/Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000
```

---

## 📊 System Workflow

```text
Candidate Upload Resume
           │
           ▼
Resume Parsing Engine
           │
           ▼
Skill Extraction
           │
           ▼
ATS Score Calculation
           │
           ▼
AI Evaluation Engine
           │
           ▼
Candidate Ranking
           │
           ▼
Database Storage
           │
           ▼
Analytics Dashboard
           │
           ▼
Interview Question Generation
```

---

## 📈 Core Modules

| Module                | Function                       |
| --------------------- | ------------------------------ |
| Resume Parser         | Extracts text from resumes     |
| ATS Engine            | Calculates compatibility score |
| Candidate Ranking     | Ranks applicants automatically |
| Skill Gap Analyzer    | Detects missing skills         |
| Dashboard Analytics   | Visual hiring insights         |
| Voice Assistant       | HR query automation            |
| Interview Generator   | AI-based interview preparation |
| Authentication System | Secure user management         |

---

## 🎯 Sample Use Case

### Job Requirement

Python Developer

Required Skills:

* Python
* Flask
* Docker

### Candidate Resume Analysis

The system automatically:

* Extracts resume text
* Identifies skills
* Compares with job requirements
* Calculates ATS score
* Detects missing skills
* Ranks the candidate
* Generates interview questions

---

## 📸 Screenshots

### Dashboard

Add screenshot here

### Candidate Analysis

Add screenshot here

### ATS Score Report

Add screenshot here

### Voice Assistant

Add screenshot here

---

## 🔮 Future Enhancements

* Semantic Search using Vector Databases
* Candidate Recommendation System
* Resume Fraud Detection
* Email Notification Automation
* Multi-Tenant Recruitment Platform
* Predictive Hiring Analytics
* AI Interview Copilot
* Cloud Deployment Support

---

## 💼 Business Impact

SmartHire AI significantly reduces manual recruitment effort by automating resume screening and candidate evaluation. It enables recruiters to:

* Reduce screening time
* Improve hiring accuracy
* Standardize candidate assessment
* Identify skill gaps quickly
* Generate interview plans automatically

---

## 👩‍💻 Author

**Ayushi Agarwal**

B.Tech Student | AI & Data Science Enthusiast

---

⭐ If you found this project useful, please consider giving it a star on GitHub!
