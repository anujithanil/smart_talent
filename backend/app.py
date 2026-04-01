from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.file_handler import save_file
from services.parser import extract_text
from services.matching_engine import match_candidate

app = Flask(__name__)
CORS(app)

# 🔥 In-memory storage (hackathon-friendly)
JOBS = []
APPLICATIONS = []


# ================================
# 🧑‍💼 ADMIN: CREATE JOB
# ================================
@app.route("/jobs", methods=["POST"])
def create_job():
    data = request.json

    job = {
        "id": len(JOBS) + 1,
        "name": data.get("name"),
        "description": data.get("description")
    }

    JOBS.append(job)

    return jsonify({
        "message": "Job created successfully",
        "job": job
    })


# ================================
# 📄 GET ALL JOBS (for dropdown)
# ================================
@app.route("/jobs", methods=["GET"])
def get_jobs():
    return jsonify(JOBS)


# ================================
# 👨‍💻 USER: APPLY TO JOB
# ================================
@app.route("/apply", methods=["POST"])
def apply_job():
    name = request.form.get("name")
    job_id = int(request.form.get("job_id"))
    file = request.files.get("resume")

    if not file:
        return jsonify({"error": "No resume uploaded"}), 400

    # Save file
    filepath = save_file(file)

    # Extract text
    text = extract_text(filepath)

    application = {
        "id": len(APPLICATIONS) + 1,
        "name": name,
        "job_id": job_id,
        "resume_filename": file.filename,
        "resume_path": filepath,
        "text": text
    }

    APPLICATIONS.append(application)

    return jsonify({
        "message": "Application submitted successfully",
        "application_id": application["id"]
    })


# ================================
# 🏆 ADMIN: GET RANKED CANDIDATES
# ================================
@app.route("/rank/<int:job_id>", methods=["GET"])
def rank_candidates(job_id):
    # Find job
    job = next((j for j in JOBS if j["id"] == job_id), None)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Get candidates for this job
    candidates = [a for a in APPLICATIONS if a["job_id"] == job_id]

    results = []

    for c in candidates:
        result = match_candidate(c["text"], job["description"])

        results.append({
            "name": c["name"],
            "resume": c["resume_filename"],
            "resume_path": c["resume_path"],
            "score": round(result["final_score"] * 100, 2),
            "justification": result.get("justification", ""),
            "hidden_gem": result.get("hidden_gem", False),

            # 🔬 Deep analysis data
            "breakdown": {
                "semantic": round(result["similarity"] * 100, 2),
                "skills": round(result["skill_score"] * 100, 2),
                "experience": result["experience"]
            }
        })

    # Sort by score
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return jsonify({
        "job": job,
        "total_candidates": len(results),
        "candidates": results
    })


# ================================
# 📄 VIEW RESUME FILE
# ================================
@app.route("/resume/<filename>", methods=["GET"])
def get_resume(filename):
    import os
    from flask import send_file

    file_path = os.path.join("uploads", filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path)


# ================================
# 🚀 RUN SERVER
# ================================
if __name__ == "__main__":
    app.run(debug=True)