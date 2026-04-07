"""
Advanced Skill Engine for Resume Analysis
Handles skill extraction, validation, and matching from structured resume data
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
import torch


class AdvancedSkillEngine:
    """Advanced skill extraction and matching engine"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Comprehensive skill database organized by category
        self.skill_database = {
            'programming_languages': [
                'python', 'java', 'c++', 'c#', 'javascript', 'typescript',
                'golang', 'rust', 'ruby', 'php', 'swift', 'kotlin',
                'scala', 'r', 'matlab', 'sql', 'sql server', 'postgresql',
                'mysql', 'mongodb', 'javascript', 'node.js'
            ],
            'frontend': [
                'react', 'vue', 'angular', 'html', 'css', 'sass', 'less',
                'bootstrap', 'tailwind', 'webpack', 'vite', 'nextjs', 'svelte'
            ],
            'backend': [
                'django', 'flask', 'spring', 'spring boot', 'fastapi',
                'express', 'asp.net', 'laravel', 'rvm', 'rails', 'grpc'
            ],
            'databases': [
                'postgresql', 'mysql', 'mongodb', 'redis', 'cassandra',
                'dynamodb', 'firestore', 'elasticsearch', 'sql server'
            ],
            'devops_cloud': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
                'github', 'gitlab', 'bitbucket', 'terraform', 'ansible'
            ],
            'ml_data': [
                'machine learning', 'deep learning', 'tensorflow', 'pytorch',
                'scikit-learn', 'pandas', 'numpy', 'data analysis',
                'nlp', 'computer vision', 'keras', 'spark'
            ],
            'soft_skills': [
                'communication', 'leadership', 'teamwork', 'problem solving',
                'project management', 'agile', 'scrum', 'analytical'
            ]
        }
    
    # ============================================
    # SKILL EXTRACTION FROM TEXT
    # ============================================
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills mentioned in resume text using pattern matching"""
        skills = []
        text_lower = text.lower()
        
        # Search for all known skills
        for category, skill_list in self.skill_database.items():
            for skill in skill_list:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        return unique_skills
    
    def extract_skills_from_structured(self, resume_data: Dict) -> List[str]:
        """Extract skills from structured resume data (priority over text extraction)"""
        skills = []
        
        # If skills section exists, use it first
        if 'skills' in resume_data and resume_data['skills']:
            skills.extend(resume_data['skills'])
        
        # Fallback to text extraction
        if not skills and 'raw_text' in resume_data:
            skills = self.extract_skills_from_text(resume_data['raw_text'])
        
        return skills
    
    # ============================================
    # SKILL VALIDATION & NORMALIZATION
    # ============================================
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name for comparison"""
        skill = skill.lower().strip()
        skill = re.sub(r'[^\w\s\+\#\.]', '', skill)
        skill = re.sub(r'\s+', ' ', skill)
        return skill
    
    def validate_skill(self, skill: str) -> bool:
        """Check if a skill is likely valid (not noise)"""
        skill = skill.strip()
        
        # Filter out very short or very long strings
        if len(skill) < 2 or len(skill) > 50:
            return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', skill):
            return False
        
        # Filter common non-skills
        excluded = ['the', 'and', 'or', 'with', 'using', 'in', 'of', 'for', 'to']
        if skill.lower() in excluded:
            return False
        
        return True
    
    def categorize_skill(self, skill: str) -> Optional[str]:
        """Categorize a skill into a category"""
        skill_normalized = self.normalize_skill(skill)
        
        for category, skills in self.skill_database.items():
            for db_skill in skills:
                if skill_normalized == db_skill or skill_normalized in db_skill:
                    return category
        
        return 'other'
    
    # ============================================
    # SEMANTIC SKILL MATCHING
    # ============================================
    
    def semantic_match_skills(self, candidate_skills: List[str], jd_skills: List[str], threshold: float = 0.6) -> Dict:
        """
        Match candidate skills to JD skills using semantic similarity
        Returns: {matched: {skill: similarity}, unmatched: [skills]}
        """
        if not candidate_skills or not jd_skills:
            return {'matched': {}, 'unmatched': jd_skills}
        
        # Clean and validate skills
        candidate_clean = [self.normalize_skill(s) for s in candidate_skills if self.validate_skill(s)]
        jd_clean = [self.normalize_skill(s) for s in jd_skills if self.validate_skill(s)]
        
        if not candidate_clean or not jd_clean:
            return {'matched': {}, 'unmatched': jd_clean}
        
        # Encode skills
        candidate_embeddings = self.model.encode(candidate_clean, convert_to_tensor=True)
        jd_embeddings = self.model.encode(jd_clean, convert_to_tensor=True)
        
        # Compute similarity matrix
        similarity_matrix = util.cos_sim(candidate_embeddings, jd_embeddings)
        
        matched = {}
        matched_jd_indices = set()
        
        # Match each JD skill to best candidate skill
        for j_idx, jd_skill in enumerate(jd_clean):
            scores = similarity_matrix[:, j_idx]
            max_score, max_idx = torch.max(scores, dim=0)
            
            if max_score > threshold:
                matched[jd_skill] = float(max_score)
                matched_jd_indices.add(j_idx)
        
        # Find unmatched JD skills
        unmatched = [jd_clean[i] for i in range(len(jd_clean)) if i not in matched_jd_indices]
        
        return {
            'matched': matched,
            'unmatched': unmatched,
            'match_percentage': len(matched) / len(jd_clean) * 100 if jd_clean else 0
        }
    
    # ============================================
    # SKILL PROFICIENCY ASSESSMENT
    # ============================================
    
    def assess_skill_proficiency(self, text: str, skill: str) -> Dict:
        """
        Assess proficiency level of a skill based on context
        Returns: {level: str, confidence: float, indicators: []}
        """
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        # Proficiency indicators
        expert_keywords = ['lead', 'architect', 'expert', 'proficient', 'mastered', 'specialized']
        senior_keywords = ['senior', 'advanced', 'in-depth', 'comprehensive', 'deep']
        mid_keywords = ['developed', 'built', 'implemented', 'strong', 'experienced']
        junior_keywords = ['familiar', 'basic', 'learning', 'exposure', 'familiarity']
        
        # Find context around skill mention
        pattern = rf'([^.]*{re.escape(skill)}[^.]*)'
        matches = re.findall(pattern, text_lower)
        
        if not matches:
            return {'level': 'unknown', 'confidence': 0, 'indicators': []}
        
        context = ' '.join(matches)
        indicators = []
        scores = {'expert': 0, 'senior': 0, 'mid': 0, 'junior': 0}
        
        for keyword in expert_keywords:
            if keyword in context:
                scores['expert'] += 1
                indicators.append(keyword)
        
        for keyword in senior_keywords:
            if keyword in context:
                scores['senior'] += 1
                indicators.append(keyword)
        
        for keyword in mid_keywords:
            if keyword in context:
                scores['mid'] += 1
                indicators.append(keyword)
        
        for keyword in junior_keywords:
            if keyword in context:
                scores['junior'] += 1
                indicators.append(keyword)
        
        # Determine level
        max_level = max(scores, key=scores.get)
        confidence = scores[max_level] / (len(indicators) + 1) if indicators else 0
        
        return {
            'skill': skill,
            'level': max_level,
            'confidence': min(confidence, 1.0),
            'indicators': indicators
        }
    
    # ============================================
    # SKILL GAPS ANALYSIS
    # ============================================
    
    def identify_skill_gaps(self, candidate_skills: List[str], jd_skills: List[str]) -> Dict:
        """
        Identify skills missing from candidate profile
        Returns: {gaps: [skills], match_score: float, priority_gaps: [skills]}
        """
        candidate_normalized = set(self.normalize_skill(s) for s in candidate_skills)
        jd_normalized = set(self.normalize_skill(s) for s in jd_skills)
        
        gaps = list(jd_normalized - candidate_normalized)
        
        # Prioritize gaps by their importance (try semantic matching)
        priority_gaps = []
        if gaps:
            match_result = self.semantic_match_skills([], gaps)  # Semantic check
            priority_gaps = [g for g in gaps if g not in match_result.get('unmatched', [])]
        
        match_score = (len(jd_normalized) - len(gaps)) / len(jd_normalized) * 100 if jd_normalized else 0
        
        return {
            'gaps': gaps,
            'gap_count': len(gaps),
            'match_score': match_score,
            'priority_gaps': priority_gaps[:5]  # Top 5 priority gaps
        }
    
    # ============================================
    # COMPREHENSIVE SKILL ANALYSIS
    # ============================================
    
    def analyze_resume_skills(self, resume_data: Dict, jd_text: str = None) -> Dict:
        """
        Perform comprehensive skill analysis on resume
        """
        analysis = {
            'extracted_skills': [],
            'skill_count': 0,
            'skill_categories': {},
            'proficiency_assessment': [],
            'jd_match': None
        }
        
        # Extract skills from structured data
        skills = self.extract_skills_from_structured(resume_data)
        validated_skills = [s for s in skills if self.validate_skill(s)]
        
        analysis['extracted_skills'] = validated_skills
        analysis['skill_count'] = len(validated_skills)
        
        # Categorize skills
        for skill in validated_skills[:15]:  # Top 15 skills
            category = self.categorize_skill(skill)
            if category not in analysis['skill_categories']:
                analysis['skill_categories'][category] = []
            analysis['skill_categories'][category].append(skill)
        
        # Assess proficiency for top skills
        for skill in validated_skills[:10]:
            proficiency = self.assess_skill_proficiency(
                resume_data.get('raw_text', ''),
                skill
            )
            analysis['proficiency_assessment'].append(proficiency)
        
        # Match against JD if provided
        if jd_text:
            from services.jd_processor import extract_keywords
            jd_skills = extract_keywords(jd_text)
            match_result = self.semantic_match_skills(validated_skills, jd_skills)
            
            analysis['jd_match'] = {
                'matched_skills': match_result['matched'],
                'unmatched_skills': match_result['unmatched'],
                'match_percentage': match_result['match_percentage'],
                'skill_gaps': self.identify_skill_gaps(validated_skills, jd_skills)
            }
        
        return analysis


# Backward compatibility wrapper functions
def compute_skill_score(text: str, jd_text: str) -> Tuple[float, List[str]]:
    """Legacy function - compute skill score for matching"""
    engine = AdvancedSkillEngine()
    
    # Extract skills from resume text
    resume_skills = engine.extract_skills_from_text(text)
    
    # Extract skills from JD
    try:
        from services.jd_processor import extract_keywords
        jd_skills = extract_keywords(jd_text)
    except:
        jd_skills = engine.extract_skills_from_text(jd_text)
    
    # Match skills
    match_result = engine.semantic_match_skills(resume_skills, jd_skills)
    matched_skills = list(match_result['matched'].keys())
    
    # Score calculation
    if jd_skills:
        score = len(matched_skills) / len(jd_skills)
    else:
        score = 0.0
    
    return score, matched_skills


def analyze_skills_advanced(resume_data: Dict, jd_text: str = None) -> Dict:
    """Advanced skill analysis for resume"""
    engine = AdvancedSkillEngine()
    return engine.analyze_resume_skills(resume_data, jd_text)
