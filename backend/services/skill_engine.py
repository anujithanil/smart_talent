from sentence_transformers import SentenceTransformer, util
import re
import torch
from services.jd_processor import extract_keywords  
model = SentenceTransformer('all-MiniLM-L6-v2')



def extract_candidate_phrases(text):
    words = re.findall(r'\b[A-Za-z\+\#\.]{2,}\b', text)
    return list(set([w.lower() for w in words]))



def semantic_match_optimized(candidate_phrases, jd_skills):
    if not candidate_phrases or not jd_skills:
        return []

    candidate_vecs = model.encode(candidate_phrases, convert_to_tensor=True)
    jd_vecs = model.encode(jd_skills, convert_to_tensor=True)

    similarity_matrix = util.cos_sim(candidate_vecs, jd_vecs)

    matched = set()

    for j_idx, jd_skill in enumerate(jd_skills):
        scores = similarity_matrix[:, j_idx]
        if torch.max(scores) > 0.6:
            matched.add(jd_skill)

    return list(matched)


# Skill strength logic
def skill_strength(text, skill):
    text = text.lower()

    if f"{skill} developer" in text:
        return 1.0
    elif f"{skill} engineer" in text:
        return 0.9
    elif f"{skill} experience" in text:
        return 0.8
    elif skill in text:
        return 0.5
    return 0


#  Final skill scoring
def compute_skill_score(text, jd_text):
    jd_skills = extract_keywords(jd_text)   # from jd_processor
    candidate_phrases = extract_candidate_phrases(text)

    matched = semantic_match_optimized(candidate_phrases, jd_skills)

    score = sum(skill_strength(text, skill) for skill in matched)

    final_score = score / (len(jd_skills) + 1)

    return final_score, matched