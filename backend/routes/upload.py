from flask import Blueprint, request, jsonify
from utils.file_handler import save_file
from services.parser import extract_text, parse_resume_structured

upload_bp = Blueprint("upload", __name__)

RESUMES = []

@upload_bp.route("/", methods=["POST"])
def upload_resumes():
    """
    Upload and parse resumes
    Supports: PDF, DOCX, PNG, JPG, JPEG
    
    Returns:
    - Backward compatible text extraction
    - Structured data (contact, experience, education, skills)
    - Metadata about extraction and sections detected
    """
    files = request.files.getlist("resumes")
    
    if not files:
        return jsonify({"error": "No files provided"}), 400
    
    resumes_data = []
    errors = []
    
    for file in files:
        try:
            # Save file
            path = save_file(file)
            
            # Extract text (backward compatible)
            text = extract_text(path)
            
            # Parse structured data
            structured_data = parse_resume_structured(path)
            
            resume_entry = {
                "filename": file.filename,
                "text": text,  # For backward compatibility
                "structured_data": structured_data
            }
            
            # Add to list
            RESUMES.append(resume_entry)
            resumes_data.append({
                "filename": file.filename,
                "status": "success",
                "text_length": len(text),
                "contact_info": structured_data.get('contact_info', {}),
                "skills": structured_data.get('skills', [])[:10],  # Top 10 skills
                "experience_count": len(structured_data.get('experience', [])),
                "education_count": len(structured_data.get('education', [])),
                "sections_detected": structured_data.get('sections_detected', {})
            })
        
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    response = {
        "message": "Upload processed",
        "total_files": len(files),
        "successful": len(resumes_data),
        "failed": len(errors),
        "resumes": resumes_data
    }
    
    if errors:
        response["errors"] = errors
    
    return jsonify(response), 200 if not errors else 206


@upload_bp.route("/resume/<int:index>", methods=["GET"])
def get_resume(index: int):
    """Get detailed structured data for a specific resume"""
    
    if 0 <= index < len(RESUMES):
        resume = RESUMES[index]
        return jsonify({
            "filename": resume["filename"],
            "structured_data": resume.get("structured_data", {}),
            "text_preview": resume.get("text", "")[:500]
        })
    
    return jsonify({"error": "Resume not found"}), 404


@upload_bp.route("/resumes", methods=["GET"])
def get_all_resumes():
    """Get summary of all uploaded resumes"""
    
    summary = []
    for idx, resume in enumerate(RESUMES):
        structured = resume.get('structured_data', {})
        summary.append({
            "index": idx,
            "filename": resume["filename"],
            "contact_info": structured.get('contact_info', {}),
            "total_skills": len(structured.get('skills', [])),
            "total_experience": len(structured.get('experience', [])),
            "total_education": len(structured.get('education', []))
        })
    
    return jsonify({
        "total_resumes": len(RESUMES),
        "resumes": summary
    })


@upload_bp.route("/clear", methods=["POST"])
def clear_resumes():
    """Clear all uploaded resumes"""
    global RESUMES
    RESUMES = []
    return jsonify({"message": "All resumes cleared"})
