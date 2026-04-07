from services.advanced_skill_engine import AdvancedSkillEngine
from services.jd_processor import extract_keywords
from typing import Dict, Tuple, List
import re
import torch


def compute_skill_score(text: str, jd_text: str) -> Tuple[float, List[str]]:
    """
    Compute skill match score between resume and job description
    Returns: (score, matched_skills)
    """
    engine = AdvancedSkillEngine()
    
    # Extract skills from resume text
    resume_skills = engine.extract_skills_from_text(text)
    
    # Extract skills from JD
    try:
        jd_skills = extract_keywords(jd_text)
    except:
        jd_skills = engine.extract_skills_from_text(jd_text)
    
    # Match skills semantically
    match_result = engine.semantic_match_skills(resume_skills, jd_skills)
    matched_skills = list(match_result['matched'].keys())
    
    # Score calculation (0-1 range)
    if jd_skills:
        score = len(matched_skills) / len(jd_skills)
    else:
        score = 0.0
    
    return score, matched_skills


def analyze_skills(text: str, jd_text: str = None) -> Dict:
    """
    Comprehensive skill analysis with proficiency assessment
    """
    engine = AdvancedSkillEngine()
    
    # Extract skills
    skills = engine.extract_skills_from_text(text)
    validated_skills = [s for s in skills if engine.validate_skill(s)]
    
    analysis = {
        'total_skills': len(validated_skills),
        'extracted_skills': validated_skills[:20],  # Top 20
        'skill_categories': {},
        'proficiency': {}
    }
    
    # Categorize skills
    for skill in validated_skills[:15]:
        category = engine.categorize_skill(skill)
        if category not in analysis['skill_categories']:
            analysis['skill_categories'][category] = []
        analysis['skill_categories'][category].append(skill)
    
    # Assess proficiency for top skills
    for skill in validated_skills[:10]:
        proficiency = engine.assess_skill_proficiency(text, skill)
        analysis['proficiency'][skill] = proficiency['level']
    
    # JD matching if provided
    if jd_text:
        analysis['jd_match'] = {
            'matched_count': 0,
            'match_score': 0.0
        }
        
        try:
            jd_skills = extract_keywords(jd_text)
            match_result = engine.semantic_match_skills(validated_skills, jd_skills)
            
            analysis['jd_match']['matched_count'] = len(match_result['matched'])
            analysis['jd_match']['match_score'] = match_result['match_percentage']
        except:
            pass
    
    return analysis


def skill_strength(text, skill):
    """Legacy function - assess skill strength"""
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


def extract_candidate_phrases(text):
    """Legacy function - extract candidate phrases"""
    words = re.findall(r'\b[A-Za-z\+\#\.]{2,}\b', text)
    return list(set([w.lower() for w in words]))
