import re
from services.advanced_experience_extractor import ExperienceExtractor
from typing import Dict, List, Tuple


def extract_experience(text):
    """
    Extract years of experience from resume text (backward compatible)
    Uses advanced extraction and returns integer
    """
    extractor = ExperienceExtractor()
    years = extractor.extract_experience_from_text(text)
    return int(years)


def extract_experience_advanced(text: str, experience_entries: List[Dict] = None) -> Dict:
    """
    Advanced experience extraction with structured data
    Returns detailed experience information including:
    - Total years of experience
    - Experience entries with dates and durations
    - Experience level (Fresher, Junior, Mid, Senior, Lead/Executive)
    - Skills-based experience breakdown
    """
    extractor = ExperienceExtractor()
    
    if experience_entries:
        total_years, enhanced_entries = extractor.extract_experience_from_structured(experience_entries)
        return {
            'total_years': total_years,
            'experience_entries': enhanced_entries,
            'level': _determine_level(total_years)
        }
    
    years = extractor.extract_experience_from_text(text)
    return {
        'total_years': years,
        'level': _determine_level(years)
    }


def _determine_level(years: float) -> str:
    """Determine experience level based on years"""
    if years < 2:
        return 'Fresher'
    elif years < 5:
        return 'Junior'
    elif years < 10:
        return 'Mid'
    elif years < 15:
        return 'Senior'
    else:
        return 'Lead/Executive'
