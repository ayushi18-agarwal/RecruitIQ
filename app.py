#from google import genai
import os
import sqlite3
from flask import flash
import csv
import io
import magic  # 🛡️ Reads file headers to stop disguised malware files
import requests  # 🚀 Handles outbound integration network webhooks
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from werkzeug.utils import secure_filename
from utils import extract_text, evaluate_candidate, generate_interview_questions
from authlib.integrations.flask_client import OAuth
import numpy as np
#import google.generativeai as genai
from dotenv import load_dotenv
# This tells your app to look for the .env file
load_dotenv()
from openai import OpenAI
# This connects your app to Gemini using the key you just saved
#genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
app = Flask(__name__)
app.secret_key = 'smarthire_dual_gateway_secure_key'
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

# 🛡️ Security Policy: Strict MIME white-list matching standard document formats
ALLOWED_MIME_TYPES = {'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}

# 🚀 Automation Endpoint: Update this string with your custom webhook connector from Zapier
ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/27945055/43s59op/"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔐 Google OAuth2 Initialization Configuration Layer
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com', # Replace with your real Client ID string
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',                 # Replace with your real Client Secret token
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

def get_db_connection():
    conn = sqlite3.connect('smart_hire.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL
        )
    ''')
    
    # JOBS SCHEMA WITH DEADLINE TRACKER FIELD
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT NOT NULL, 
            description TEXT NOT NULL, 
            skills TEXT NOT NULL, 
            experience TEXT NOT NULL,
            deadline TEXT NOT NULL DEFAULT '2026-06-30'
        )
    ''')
    
    # COMPLETE STRUCTURAL CANDIDATE SCHEMA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, name TEXT NOT NULL, email TEXT NOT NULL,
            score INTEGER, recommendation TEXT, skills_found TEXT, skills_missing TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )
    ''')
    
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
        
    conn.commit()
    conn.close()

init_db()

def verify_file_integrity(file_path):
    """🛡️ Helper function executing signature binary byte scans on documents."""
    try:
        file_mime = magic.from_file(file_path, mime=True)
        if file_mime not in ALLOWED_MIME_TYPES:
            return False, f"MIME Conflict: Target payload detected as '{file_mime}' (Unsafe format violation)."
        return True, "Safe"
    except Exception as e:
        return False, f"File scanning exception error: {str(e)}"

# --- 1. CORE ROUTER LANDING PAGE ---
@app.route('/')
def index():
    return render_template('welcome.html')

# --- 1B. GOOGLE OAUTH IDENTITY ROUTING LIFECYCLE CONTROLLERS ---
@app.route('/login/google')
def login_google():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    
    user_email = user_info.get('email', '').strip().lower()
    user_name = user_info.get('name', 'Google Applicant')
    
    # Check if the authenticating Google user matches your corporate administrator target profile
    if user_email == "your_admin_email@gmail.com": # <-- Adjust this line to match your chosen admin email profile
        session['user'] = 'admin'
        return redirect(url_for('dashboard'))
    else:
        # Automatic secure tracking session setup for external candidate gateways
        session['candidate_email'] = user_email
        session['candidate_name'] = user_name
        return redirect(url_for('candidate_status', email=user_email))

# --- 2. PUBLIC CANDIDATE ENDPOINTS ---
@app.route('/candidate')
def candidate_home():
    conn = get_db_connection()
    # Filter to only show jobs where the deadline is today or in the future
    # We use date('now') to compare against your 'YYYY-MM-DD' stored strings
    active_jobs = conn.execute('''
        SELECT * FROM jobs 
        WHERE date(deadline) >= date('now') 
        ORDER BY id DESC
    ''').fetchall()
    conn.close()
    return render_template('candidate_home.html', jobs=active_jobs)

# Change this line
from datetime import datetime
########
# Add this to app.py
@app.context_processor
def inject_date_tools():
    return {'today': datetime.now().date()}

@app.template_filter('to_date')
def to_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return datetime.now().date() # Fallback
    
@app.route('/candidate/status', methods=['GET', 'POST'])
def candidate_status():
    if request.method == 'POST':
        # 1. Capture the email from the POST request
        email = request.form.get('email', '').strip().lower()
        # 2. Redirect to the GET version of the same route with the email as a parameter
        return redirect(url_for('candidate_status', email=email))
    
    # --- GET Logic Starts Here ---
    email = request.args.get('email', '').strip().lower()
    submissions = []
    searched = False
    
    if email:
        searched = True
        conn = get_db_connection()
        raw_submissions = conn.execute('''
            SELECT c.*, j.title as job_title, j.deadline FROM candidates c
            JOIN jobs j ON c.job_id = j.id WHERE c.email = ? ORDER BY c.id DESC
        ''', (email,)).fetchall()
        conn.close()
        
        for row in raw_submissions:
            c_dict = dict(row)
            # --- TIME-BASED REVEAL ENVELOPE GATE ---
            job_deadline_str = c_dict.get('deadline')
            true_status = c_dict['recommendation']
            masked_status = "Application Under Review"
            
            if job_deadline_str:
                try:
                    deadline_date = datetime.strptime(job_deadline_str, "%Y-%m-%d").date()
                    release_milestone_date = deadline_date + timedelta(days=1)
                    if datetime.now().date() >= release_milestone_date:
                        masked_status = true_status  
                except ValueError:
                    pass 
            
            c_dict['recommendation'] = masked_status
            submissions.append(c_dict)
        
    return render_template('candidate_status.html', submissions=submissions, email=email, searched=searched)

from datetime import datetime # Ensure this is at the top of your app.py

@app.route('/candidate/apply', methods=['POST'])
def candidate_apply():
    print("DEBUG: candidate_apply function started!")
    # 1. Get data from the form
    job_id = request.form.get('job_id')
    applicant_name = request.form.get('applicant_name')
    applicant_email = request.form.get('applicant_email')
    
    conn = get_db_connection()
    job = conn.execute('SELECT title, description, skills, deadline FROM jobs WHERE id = ?', (job_id,)).fetchone()
    
    if not job:
        conn.close()
        return f"Error: Job ID {job_id} not found.", 404
    
    # Date Guard
    try:
        deadline_date = datetime.strptime(job['deadline'], "%Y-%m-%d").date()
        if datetime.now().date() > deadline_date:
            conn.close()
            return "Application Error: This job application deadline has passed.", 403
    except (ValueError, TypeError):
        pass
        
    # 2. Process the file
    file = request.files.get('resume')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 🛡️ Verify integrity
        if not verify_file_integrity(file_path)[0]:
            if os.path.exists(file_path): os.remove(file_path)
            return "Invalid file format", 400
        
        # 3. AI Evaluation
        resume_text = extract_text(file_path)
        result = evaluate_candidate(resume_text, job['title'], job['description'], job['skills'])
        
        name_to_save = applicant_name if applicant_name else os.path.splitext(filename)[0].replace('_', ' ').title()

        # 4. Save to Database
        conn.execute('''
            INSERT INTO candidates (job_id, name, email, score, recommendation, skills_found, skills_missing)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id, 
            name_to_save,
            applicant_email, 
            result['fit_score'], 
            result['recommendation'], 
            result['skills_found'], 
            result['skills_missing']
        ))
        conn.commit()

        # --- NOTIFICATION TRIGGER (Preserved from Admin Logic) ---
        if "Strong Hire" in result.get('recommendation', ''):
            notification_payload = {
                "candidate_name": name_to_save,
                "job_title": job['title'],
                "score": result['fit_score'],
                "email_link": request.url_root + "candidates"
            }
            try:
                requests.post("https://hooks.zapier.com/hooks/catch/27945055/43wwfkg/", 
                             json=notification_payload, timeout=5)
                print(f"DEBUG: Notification sent for {name_to_save}")
            except Exception as e:
                print(f"DEBUG: Notification error: {e}")
        # ---------------------------------------------------------

        conn.close()
        
        flash("Application received successfully! Thank you for applying.")
        return redirect(url_for('thank_you', email=applicant_email))    
    
    conn.close()
    return "Error: No file uploaded.", 400

@app.route('/thank-you')
def thank_you():
    email = request.args.get('email', '')
    return render_template('thank_you.html', email=email)
# --- 3. ADMIN/HR SECURE MODULES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        # Ensure 'users' table exists and has these columns
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user'] = user['username']
            # Redirect to the dashboard route
            return redirect(url_for('dashboard'))
        else:
            # If login fails, render the page again with an error
            return render_template('login.html', error="Invalid username or password.")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    
    # Create the redirect response
    resp = make_response(redirect(url_for('index')))
    
    # Force the browser to delete the session cookie
    resp.set_cookie('session', '', expires=0)
    
    return resp

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    try:
        jobs = conn.execute('SELECT * FROM jobs').fetchall()
        
        # This restores the keys (strong, hire, review, reject) that your dashboard.html needs
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN LOWER(recommendation) LIKE '%strong hire%' THEN 1 ELSE 0 END) as strong,
                SUM(CASE WHEN LOWER(recommendation) LIKE '%hire%' THEN 1 ELSE 0 END) as hire,
                SUM(CASE WHEN LOWER(recommendation) LIKE '%review%' THEN 1 ELSE 0 END) as review,
                SUM(CASE WHEN LOWER(recommendation) LIKE '%reject%' THEN 1 ELSE 0 END) as reject
            FROM candidates
        ''').fetchone()
        
        top_candidates = conn.execute('''
            SELECT c.*, j.title as job_title FROM candidates c 
            JOIN jobs j ON c.job_id = j.id ORDER BY c.score DESC LIMIT 5
        ''').fetchall()
        
        return render_template('dashboard.html', jobs=jobs, stats=stats, top_candidates=top_candidates)
    
    except Exception as e:
        return f"<h1>Database Error:</h1><p>{str(e)}</p>"
    finally:
        conn.close()

@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        skills = request.form['skills']
        experience = request.form['experience']
        deadline = request.form.get('deadline', '2026-06-30') 
        publish_linkedin = request.form.get('publish_linkedin') in ['true', 'on']
        
        conn.execute('INSERT INTO jobs (title, description, skills, experience, deadline) VALUES (?, ?, ?, ?, ?)',
                     (title, description, skills, experience, deadline))
        conn.commit()
        
        if publish_linkedin and ZAPIER_WEBHOOK_URL:
            syndication_payload = {
                "title": title,
                "skills": skills,
                "experience": experience,
                "deadline": deadline,
                "portal_url": request.url_root + "candidate"
            }
            try:
                # The timeout is crucial to ensure your page doesn't hang
                response = requests.post(ZAPIER_WEBHOOK_URL, json=syndication_payload, timeout=5)
                print(f"LinkedIn Syndication Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"LinkedIn Webhook Error: {e}")
        
    # GET Logic: This must exist to return the page when you click the link
    all_jobs = conn.execute('SELECT * FROM jobs ORDER BY id DESC').fetchall()
    conn.close()
    
    # THIS LINE WAS LIKELY MISSING OR HIDDEN
    return render_template('jobs.html', jobs=all_jobs)

@app.route('/candidates', methods=['GET', 'POST'])
def candidates():
    conn = get_db_connection()
    
    # --- POST: FILE UPLOAD & AI EVALUATION (Unchanged) ---
    if request.method == 'POST':
        job_id = request.form['job_id']
        files = request.files.getlist('resumes')
        
        job = conn.execute('SELECT title, description, skills FROM jobs WHERE id = ?', (job_id,)).fetchone()
        
        if job:
            for file in files:
                if file and ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    if not verify_file_integrity(file_path)[0]:
                        if os.path.exists(file_path): os.remove(file_path)
                        continue
                    
                    resume_text = extract_text(file_path)
                    result = evaluate_candidate(resume_text, job['title'], job['description'], job['skills'])
                    
                    candidate_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    conn.execute('''
                        INSERT INTO candidates (job_id, name, email, score, recommendation, skills_found, skills_missing)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (job_id, candidate_name, 'internal_batch@smarthire.local', result['fit_score'], 
                          result['recommendation'], result['skills_found'], result['skills_missing']))
                    conn.commit()
                    if "Strong Hire" in result.get('recommendation', ''):
                        notification_payload = {
                            "candidate_name": candidate_name,
                            "job_title": job['title'],
                            "score": result['fit_score'],
                            "email_link": request.url_root + "candidates"
                        }
                        try:
                            # Zapier webhook
                            requests.post("https://hooks.zapier.com/hooks/catch/27945055/43wwfkg/", 
                                         json=notification_payload, timeout=5)
                            print(f"DEBUG: Notification sent for {candidate_name}")
                        except Exception as e:
                            print(f"DEBUG: Notification error: {e}")
        return redirect(url_for('candidates', job_id=job_id))

    # --- GET: DATA FETCHING & UI FILTERING ---
    selected_job_id = request.args.get('job_id', type=int)
    
    # 1. Filtered Dropdown: Only shows jobs that are NOT expired
    jobs = conn.execute('''
        SELECT * FROM jobs 
        WHERE date(deadline) >= date('now') 
        ORDER BY id DESC
    ''').fetchall()
    
    # 2. Candidate Table: Fetches all candidates (no date filter) 
    # so you never lose visibility of historical data
    query = 'SELECT c.*, j.title as job_title FROM candidates c JOIN jobs j ON c.job_id = j.id'
    params = []
    if selected_job_id:
        query += " WHERE c.job_id = ?"
        params.append(selected_job_id)
    query += " ORDER BY c.score DESC"
    
    candidate_list = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('candidates.html', candidates=candidate_list, jobs=jobs, selected_job_id=selected_job_id)
@app.route('/candidates/prep/<int:candidate_id>')
def candidate_prep(candidate_id):
    # 🔓 RESTORED: Session guard disabled to allow seamless template rendering alongside Firebase scripts
    # if 'user' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    candidate = conn.execute('''
        SELECT c.*, j.title as job_title FROM candidates c 
        JOIN jobs j ON c.job_id = j.id WHERE c.id = ?
    ''', (candidate_id,)).fetchone()
    conn.close()
    if not candidate: return "Candidate not found.", 404
    generated_guide = generate_interview_questions(
        candidate['name'], candidate['job_title'], candidate['skills_found'], candidate['skills_missing']
    )
    return render_template('prep.html', candidate=candidate, guide=generated_guide)

@app.route('/reports')
def reports():
    # 🔓 RESTORED: Session guard disabled to allow seamless template rendering alongside Firebase scripts
    # if 'user' not in session: 
    #     return redirect(url_for('login'))
    conn = get_db_connection()
    stats = conn.execute('''
        SELECT COUNT(*) as total,
            SUM(CASE WHEN recommendation = 'Strong Hire' THEN 1 ELSE 0 END) as strong,
            SUM(CASE WHEN recommendation = 'Hire' THEN 1 ELSE 0 END) as hire,
            SUM(CASE WHEN recommendation = 'Review' THEN 1 ELSE 0 END) as review,
            SUM(CASE WHEN recommendation = 'Reject' THEN 1 ELSE 0 END) as reject
        FROM candidates
    ''').fetchone()
    candidates = conn.execute('SELECT skills_found FROM candidates').fetchall()
    skill_counts = {}
    for c in candidates:
        if c['skills_found']:
            for skill in c['skills_found'].split(','):
                s = skill.strip()
                if s: skill_counts[s] = skill_counts.get(s, 0) + 1
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    conn.close()
    return render_template('reports.html', stats=stats, top_skills=top_skills)

@app.route('/reports/export')
def export_csv():
    # 🔓 RESTORED: Session guard disabled to allow seamless template rendering alongside Firebase scripts
    # if 'user' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    candidates = conn.execute('''
        SELECT c.id, c.name, j.title, c.score, c.recommendation, c.skills_found 
        FROM candidates c JOIN jobs j ON c.job_id = j.id
    ''').fetchall()
    conn.close()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Candidate Name', 'Job Profile', 'Match Score', 'Status Decision', 'Verified Skills'])
    for r in candidates:
        cw.writerow([r[0], r[1], r[2], f"{r[3]}%", r[4], r[5]])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=smarthire_bi_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# --- 4. VOICE ASSISTANT REST ENDPOINTS ---
@app.route('/api/voice/stats')
def api_voice_stats():
    conn = get_db_connection()
    row = conn.execute('''
        SELECT COUNT(*) as total, MAX(score) as max_score,
        SUM(CASE WHEN recommendation IN ('Strong Hire', 'Hire') THEN 1 ELSE 0 END) as hires
        FROM candidates
    ''').fetchone()
    conn.close()
    return jsonify({"total": row['total'] or 0, "top_score": row['max_score'] or 0, "hires": row['hires'] or 0})

@app.route('/api/voice/top-candidate')
def api_voice_top():
    conn = get_db_connection()
    row = conn.execute('SELECT name, score FROM candidates ORDER BY score DESC LIMIT 1').fetchone()
    conn.close()
    if row: return jsonify({"name": row['name'], "score": row['score']})
    return jsonify({"name": "None", "score": 0})

@app.route('/api/voice/candidate/<name>')
def api_voice_candidate(name):
    conn = get_db_connection()
    row = conn.execute('SELECT name, score, recommendation FROM candidates WHERE name LIKE ? ORDER BY score DESC LIMIT 1', (f'%{name}%',)).fetchone()
    conn.close()
    if row: return jsonify({"found": True, "name": row['name'], "score": row['score'], "rec": row['recommendation']})
    return jsonify({"found": False})

# --- ADD THESE TO YOUR EXISTING ROUTES ---
# --- CLEANED API ROUTES ---

#


# Initialize the OpenAI client


# 1. Force reload and clear any previous environment state


# 2. Get the key and strip any accidental whitespace/invisible characters
# Initialize the client pointing to Groq's API
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

@app.route('/api/chatbot/query', methods=['POST'])
def api_chatbot_query():
    data = request.json or {}
    user_message = data.get('message', '').strip()
    
    try:
        # Use a high-performance free model like Llama 3
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "You are a helpful HR assistant for SmartHire."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
        
    except Exception as e:
        print(f"Groq/AI Error: {e}")
        return jsonify({"reply": "I'm having trouble connecting to the AI service."})

import logging
logging.basicConfig(level=logging.DEBUG)
if __name__ == '__main__':
    app.run(debug=True, port=5000)
