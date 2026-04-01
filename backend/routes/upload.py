from flask import Blueprint, request, jsonify
from utils.file_handler import save_file
from services.parser import extract_text

upload_bp = Blueprint("upload", __name__)

RESUMES = []

@upload_bp.route("/", methods=["POST"])
def upload_resumes():
    files = request.files.getlist("resumes")

    for file in files:
        path = save_file(file)
        text = extract_text(path)

        RESUMES.append({
            "filename": file.filename,
            "text": text
        })

    return jsonify({
        "message": "Upload successful",
        "total_resumes": len(RESUMES)
    })