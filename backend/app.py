from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from services.jd_processor import extract_keywords
from db import get_connection
from utils.file_handler import save_file
from services.parser import extract_text, parse_resume_structured
from services.matching_engine import match_candidate
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:5173"]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)
app.config["CORS_HEADERS"] = "Content-Type"

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    response = jsonify({"error": str(e)})
    response.status_code = 500
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response


# ================================
#  ADMIN: CREATE JOB
# ================================
@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json

    if data["username"] == "admin" and data["password"] == "admin123":
        token = create_access_token(identity="admin")
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401
@app.route("/jobs", methods=["POST"])
@jwt_required()
def create_job():
    data = request.json
    name=data.get("name")
    description=data.get("description")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO jobs (name, description) VALUES (%s, %s)",
    (name, description))
    conn.commit()

    job_id = cursor.lastrowid

    return jsonify({
        "id": job_id,
        "name": name,
        "description": description
    })

# ================================
#  GET ALL JOBS (for dropdown)
# ================================
@app.route("/jobs", methods=["GET"])
def get_jobs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    return jsonify(jobs)


# ================================
#  USER: APPLY TO JOB
# ================================
@app.route("/apply", methods=["POST", "OPTIONS"])
def apply_job():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        return response

    name = request.form.get("name")
    job_id = request.form.get("job_id")
    file = request.files.get("resume")

    if not file:
        response = jsonify({"error": "No resume uploaded"})
        response.status_code = 400
        return response

    try:
        job_id = int(job_id)
    except (TypeError, ValueError):
        response = jsonify({"error": "Invalid job_id"})
        response.status_code = 400
        return response

    # Save file
    filepath = save_file(file)

    # Extract text using structured parser
    text = ""
    extraction_errors = []
    try:
        parsed_resume = parse_resume_structured(filepath)
        if isinstance(parsed_resume, dict) and parsed_resume.get('status') == 'error':
            extraction_errors.append(parsed_resume.get('error', 'Unknown parser error'))
            text = parsed_resume.get('raw_text', '') or ''
        else:
            text = parsed_resume.get('raw_text', '') if isinstance(parsed_resume, dict) else ''

        if not text:
            text = extract_text(filepath)
    except Exception as exc:
        print(f"Resume parsing failed: {exc}")
        extraction_errors.append(str(exc))
        text = extract_text(filepath)

    if not text and extraction_errors:
        print(f"Resume extraction errors: {extraction_errors}")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO applications (name, job_id, resume_filename, resume_path, resume_text) VALUES (%s, %s, %s, %s, %s)",
        (name, job_id, file.filename, filepath, text)
    )
    conn.commit()

    application_id = cursor.lastrowid
    cursor.close()
    conn.close()

    response_payload = {
        "message": "Application submitted successfully",
        "application_id": application_id
    }
    if not text and extraction_errors:
        response_payload["warning"] = "No text could be extracted from the resume. Install Tesseract OCR or use a selectable-text PDF."
        response_payload["errors"] = extraction_errors

    response = jsonify(response_payload)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response

def compute_missing_skills(jd_text, candidates):
    jd_skills = extract_keywords(jd_text)
    jd_skill_freq = {}
    for skill in jd_skills:
        jd_skill_freq[skill] = jd_skill_freq.get(skill, 0) + 1

    if not candidates:
        return [{"skill": skill, "severity": 1.0} for skill in list(jd_skill_freq.keys())[:5]]

    skill_count = {}
    for c in candidates:
        skills = set(extract_keywords(c["resume_text"]))
        for s in skills:
            skill_count[s] = skill_count.get(s, 0) + 1

    missing = []
    for skill, jd_count in jd_skill_freq.items():
        candidate_count = skill_count.get(skill, 0)
        coverage = candidate_count / len(candidates)
        if coverage < 0.4:
            severity = (jd_count / len(jd_skills)) * (1 - coverage)
            missing.append({"skill": skill, "severity": round(severity, 2)})

    return sorted(missing, key=lambda x: x["severity"], reverse=True)[:5]
def generate_summary(jd_text, candidates, scores):
    if not candidates:
        return "No candidate data yet. Once resumes are received, this panel will highlight the strongest skills and most common gaps."

    jd_skills = extract_keywords(jd_text)

    skill_freq = {}
    experience_sum = 0

    for c in candidates:
        skills = extract_keywords(c["resume_text"])
        for s in skills:
            skill_freq[s] = skill_freq.get(s, 0) + 1

        from services.experience_extractor import extract_experience
        experience_sum += extract_experience(c["resume_text"])

    

    avg = sum(scores) / len(scores) if scores else 0
    avg_experience = experience_sum / len(candidates) if candidates else 0

    level = "strong" if avg > 0.7 else "moderate" if avg > 0.4 else "weak"
    experience_comment = (
        f"The applicant pool has an average of {avg_experience:.1f} years of experience." if avg_experience >= 4 else
        f"Most candidates are early career or mid-level with {avg_experience:.1f} years of experience." if avg_experience >= 2 else
        f"The current pipeline is largely entry-level with {avg_experience:.1f} years of experience."
    )

    return f"""
    The current candidate pool is {level} for this role.
    {experience_comment}
   
    """
# ================================
#  ADMIN: GET RANKED CANDIDATES
# ================================
@app.route("/rank/<int:job_id>", methods=["GET"])
@jwt_required()
def rank_candidates(job_id):
    from services.parser import parse_resume_structured
    import json
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get job
    cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()

    # Get applications
    cursor.execute("SELECT * FROM applications WHERE job_id = %s", (job_id,))
    candidates = cursor.fetchall()

    results = []

    for c in candidates:
        # Try to get structured data by re-parsing the resume file
        resume_data = None
        try:
            if c.get("resume_path"):
                resume_data = parse_resume_structured(c["resume_path"])
        except Exception as e:
            print(f"Warning: Could not parse structured data for {c['name']}: {e}")
        
        # Pass structured data for intelligent experience extraction
        result = match_candidate(c["resume_text"], job["description"], resume_data=resume_data)

        results.append({
            "name": c["name"],
            "resume": c["resume_filename"],
            "score": round(result["final_score"] * 100, 2),
            "justification": result.get("justification", ""),
            "hidden_gem": result.get("hidden_gem", False),
            "matched_skills": result.get("matched_skills", []),
            "interview_guide": result.get("interview_guide", {}),
            "breakdown": {
                "semantic": round(result["similarity"] * 100, 2),
                "skills": round(result["skill_score"] * 100, 2),
                "experience": result["experience"]
            }
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return jsonify(results)
@app.route("/top-candidates/<int:job_id>", methods=["GET"])
@jwt_required()
def top_candidates(job_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get job
    cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()

    # Get candidates
    cursor.execute("SELECT * FROM applications WHERE job_id = %s", (job_id,))
    candidates = cursor.fetchall()

    results = []

    for c in candidates:
        result = match_candidate(c["resume_text"], job["description"])

        results.append({
            "name": c["name"],
            "score": result["final_score"],
            "justification": result["justification"]
        })

    # Sort + take top 5
    top = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

    return jsonify(top)

# ================================
#  VIEW RESUME FILE
# ================================
@app.route("/resume/<filename>", methods=["GET"])
def get_resume(filename):
    import os
    from flask import send_file

    file_path = os.path.join("uploads", filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path)

@app.route("/insights/<int:job_id>", methods=["GET"])
@jwt_required()
def hiring_insights(job_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM jobs WHERE id=%s", (job_id,))
    job = cursor.fetchone()

    cursor.execute("SELECT * FROM applications WHERE job_id=%s", (job_id,))
    candidates = cursor.fetchall()

    scores = []
    experiences = []
    skill_counter = {}

    for c in candidates:
        result = match_candidate(c["resume_text"], job["description"])
        scores.append(result["final_score"])
        experiences.append(result["experience"])

        for skill in result.get("matched_skills", []):
            skill_counter[skill] = skill_counter.get(skill, 0) + 1

    avg_score = sum(scores) / len(scores) if scores else 0

    jd_skills = extract_keywords(job["description"])
    STOPWORDS = {"the", "is", "and", "we", "a", "to", "of", "in", "on"}

    missing_skills = [
        skill for skill in jd_skills
        if skill_counter.get(skill, 0) < len(candidates) * 0.3
        and skill not in STOPWORDS
        and len(skill) > 3
    ]

    top_skill = max(skill_counter, key=skill_counter.get) if skill_counter else "N/A"

    summary = generate_summary(job["description"], candidates, scores)

    top_skills = [skill for skill, _ in sorted(skill_counter.items(), key=lambda x: x[1], reverse=True)[:5]]
    missing_skills = compute_missing_skills(job["description"], candidates)

    response = jsonify({
        "total_candidates": len(candidates),
        "average_score": round(avg_score * 100, 2),
        "max_score": round(max(scores) * 100, 2) if scores else 0,
        "min_score": round(min(scores) * 100, 2) if scores else 0,
        "avg_experience": sum(experiences) / len(experiences) if experiences else 0,
        "summary": summary.strip(),
        "top_skills": top_skills,
        "missing_skills": missing_skills[:5],
        "skill_distribution": skill_counter
    })

    return response

@app.route("/intelligence/<int:job_id>", methods=["GET"])
@jwt_required()
def recruiter_intelligence(job_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM jobs WHERE id=%s", (job_id,))
    job = cursor.fetchone()

    cursor.execute("SELECT * FROM applications WHERE job_id=%s", (job_id,))
    candidates = cursor.fetchall()

    skill_counter = {}
    exp_levels = {"beginner": 0, "mid": 0, "senior": 0}

    for c in candidates:
        result = match_candidate(c["resume_text"], job["description"])

        # Count skills
        for skill in result["matched_skills"]:
            skill_counter[skill] = skill_counter.get(skill, 0) + 1

        # Experience distribution
        exp = result["experience"]
        if exp < 2:
            exp_levels["beginner"] += 1
        elif exp < 5:
            exp_levels["mid"] += 1
        else:
            exp_levels["senior"] += 1

    # Missing skills detection
    missing_skills = compute_missing_skills(job["description"], candidates)

    total_candidates = len(candidates)
    exp_percentages = {
        "beginner": round((exp_levels["beginner"] / total_candidates) * 100, 1) if total_candidates else 0,
        "mid": round((exp_levels["mid"] / total_candidates) * 100, 1) if total_candidates else 0,
        "senior": round((exp_levels["senior"] / total_candidates) * 100, 1) if total_candidates else 0,
    }

    return jsonify({
        "total_candidates": total_candidates,
        "skill_distribution": skill_counter,
        "missing_skills": missing_skills[:5],
        "experience_distribution": {
            "counts": exp_levels,
            "percentages": exp_percentages
        }
    })
# ================================
#  RUN SERVER
# ================================
if __name__ == "__main__":
    app.run(debug=True)