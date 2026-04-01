from services.nlp_engine import compute_chunked_similarity, compute_similarity
from services.skill_engine import compute_skill_score
from services.experience_extractor import extract_experience
from services.scorer import calculate_score
from services.justification_engine import generate_justification, detect_hidden_gem
from services.nlp_engine import compute_chunked_similarity

def match_candidate(resume_text, jd_text):

    similarity = compute_chunked_similarity(resume_text, jd_text)

    skill_score, matched_skills = compute_skill_score(resume_text, jd_text)

    years = extract_experience(resume_text)

    final_score = calculate_score(similarity, years, skill_score)

    result = {
        "similarity": similarity,
        "skill_score": skill_score,
        "experience": years,
        "matched_skills": matched_skills,
        "final_score": final_score
    }

    # Add justification
    result["justification"] = generate_justification(result, jd_text)

    # Hidden gem detection
    result["hidden_gem"] = detect_hidden_gem(similarity, skill_score)

    return result