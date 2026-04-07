from flask import Blueprint, request, jsonify
from routes.upload import RESUMES
from services.matching_engine import match_candidate

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/", methods=["POST"])
def rank_candidates():
    data = request.json
    job_description = data.get("jd")

    results = []

    for resume in RESUMES:
        # Extract structured data if available
        resume_data = resume.get("structured_data", None)
        
        result = match_candidate(resume["text"], job_description, resume_data=resume_data)

        summary = f"{len(result['matched_skills'])} skills matched, {result['experience']} years experience."

        results.append({
            "name": resume["filename"],
            "score": round(result["final_score"] * 100, 2),
            "experience": result["experience"],
            "matched_skills": result["matched_skills"],
            "justification": result["justification"],
            "hidden_gem": result["hidden_gem"]
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return jsonify(results)