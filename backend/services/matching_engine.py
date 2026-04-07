from services.nlp_engine import compute_chunked_similarity
from services.skill_engine import compute_skill_score
from services.experience_extractor import extract_experience, extract_experience_advanced
from services.scorer import calculate_score
from services.justification_engine import generate_justification, detect_hidden_gem, generate_interview_guide
from typing import Dict, Optional, List


def match_candidate(resume_text: str, jd_text: str, resume_data: Optional[Dict] = None) -> Dict:
    """
    Match candidate resume against job description
    
    Args:
        resume_text: Raw text from resume (legacy)
        jd_text: Job description text
        resume_data: Structured resume data (optional, for enhanced matching)
    
    Returns:
        Matching result with scores and analysis
    """
    
    # Compute similarity
    similarity = compute_chunked_similarity(resume_text, jd_text)
    
    # Compute skill score
    skill_score, matched_skills = compute_skill_score(resume_text, jd_text)
    
    # Extract experience
    years = extract_experience(resume_text)
    
    # Use structured data if available for enhanced experience extraction
    if resume_data and 'experience' in resume_data and resume_data['experience']:
        try:
            experience_detail = extract_experience_advanced(resume_data)
            years = experience_detail.get('total_years', years)
            experience_level = experience_detail.get('level', 'Unknown')
        except Exception as e:
            print(f"Error extracting experience from structured data: {e}")
            experience_level = 'Unknown'
    else:
        experience_level = 'Unknown'
    
    # Calculate final score
    final_score = calculate_score(similarity, years, skill_score)
    
    # Build result
    result = {
        "similarity": similarity,
        "skill_score": skill_score,
        "experience": years,
        "experience_level": experience_level,
        "matched_skills": matched_skills,
        "final_score": final_score
    }
    
    # Add justification
    result["justification"] = generate_justification(result, jd_text)
    
    # Hidden gem detection
    result["hidden_gem"] = detect_hidden_gem(similarity, skill_score)
    result["interview_guide"] = generate_interview_guide(result, resume_text, jd_text)

    # Add structured data insights if available
    if resume_data:
        result["candidate_info"] = {
            "email": resume_data.get('contact_info', {}).get('email', 'N/A'),
            "skills_count": len(resume_data.get('skills', [])),
            "education_entries": len(resume_data.get('education', [])),
            "experience_entries": len(resume_data.get('experience', []))
        }
    
    return result


def match_candidate_advanced(resume_data: Dict, jd_text: str) -> Dict:
    """
    Advanced matching using structured resume data
    Provides more detailed analysis
    """
    
    raw_text = resume_data.get('raw_text', '')
    
    # Use the standard matching function
    result = match_candidate(raw_text, jd_text, resume_data)
    
    # Add additional insights from structured data
    result["resume_metadata"] = resume_data.get('metadata', {})
    result["parsed_sections"] = resume_data.get('sections_detected', {})
    
    # Add education insights
    education_entries = resume_data.get('education', [])
    if education_entries:
        result["education_background"] = {
            'count': len(education_entries),
            'degrees': [e.get('degree', '') for e in education_entries],
            'institutions': [e.get('institution', '') for e in education_entries]
        }
    
    return result
