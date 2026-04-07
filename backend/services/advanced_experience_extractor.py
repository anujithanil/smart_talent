"""
Advanced Experience Extraction from Resume Data
Handles various date formats and calculates accurate years of experience
"""

import re
from datetime import datetime
from typing import Dict, Tuple, Optional, List
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta


class ExperienceExtractor:
    """Advanced extraction of professional experience and years calculation"""
    
    def __init__(self):
        self.month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
    
    # ============================================
    # DATE PARSING
    # ============================================
    
    def parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse various date string formats"""
        if not date_str or not isinstance(date_str, str):
            return None
        
        date_str = date_str.strip().lower()
        
        # Check for "Present" or "Current"
        if date_str in ['present', 'current', 'ongoing']:
            return datetime.now()
        
        try:
            # Try dateutil parser first (handles most formats)
            return parse_date(date_str, fuzzy=True)
        except:
            pass
        
        # Custom patterns for common formats
        patterns = [
            # "Month Year" or "Month YYYY"
            (r'([a-z]+)\s*(\d{4})', self._parse_month_year),
            # "MM/YYYY" or "M/YYYY"
            (r'(\d{1,2})/(\d{4})', self._parse_slash_format),
            # "YYYY-MM" or "YYYY-MM-DD"
            (r'(\d{4})-(\d{1,2})(?:-(\d{1,2}))?', self._parse_iso_format),
            # Just year "YYYY"
            (r'^(\d{4})$', self._parse_year_only),
        ]
        
        for pattern, parser_func in patterns:
            match = re.search(pattern, date_str)
            if match:
                return parser_func(match)
        
        return None
    
    def _parse_month_year(self, match) -> Optional[datetime]:
        """Parse 'Month Year' format"""
        month_str = match.group(1)
        year_str = match.group(2)
        
        month = self.month_map.get(month_str, None)
        if month and year_str.isdigit():
            try:
                return datetime(int(year_str), month, 1)
            except:
                return None
        return None
    
    def _parse_slash_format(self, match) -> Optional[datetime]:
        """Parse 'MM/YYYY' format"""
        month_str = match.group(1)
        year_str = match.group(2)
        
        try:
            month = int(month_str)
            year = int(year_str)
            if 1 <= month <= 12 and 1900 <= year <= 2100:
                return datetime(year, month, 1)
        except:
            pass
        return None
    
    def _parse_iso_format(self, match) -> Optional[datetime]:
        """Parse 'YYYY-MM(-DD)' format"""
        year_str = match.group(1)
        month_str = match.group(2)
        day_str = match.group(3)
        
        try:
            year = int(year_str)
            month = int(month_str)
            day = int(day_str) if day_str else 1
            
            if 1900 <= year <= 2100 and 1 <= month <= 12:
                return datetime(year, month, day)
        except:
            pass
        return None
    
    def _parse_year_only(self, match) -> Optional[datetime]:
        """Parse year-only format 'YYYY'"""
        try:
            year = int(match.group(1))
            if 1900 <= year <= 2100:
                return datetime(year, 1, 1)
        except:
            pass
        return None
    
    # ============================================
    # EXPERIENCE EXTRACTION
    # ============================================
    
    def extract_experience_period(self, period_str: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Extract start and end dates from period string
        Handles: "Jan 2020 - Present", "2020-2023", "Jan 2020 - Mar 2021", etc.
        """
        if not period_str:
            return None, None
        
        # Split by common separators
        separators = [' - ', ' – ', '-', '–', ' to ']
        parts = None
        
        for sep in separators:
            if sep in period_str:
                parts = [p.strip() for p in period_str.split(sep)]
                break
        
        if not parts or len(parts) < 2:
            # Try single date
            start_date = self.parse_date_string(period_str)
            return start_date, None
        
        start_date = self.parse_date_string(parts[0])
        end_date = self.parse_date_string(parts[1])
        
        return start_date, end_date
    
    def calculate_months_duration(self, start_date: datetime, end_date: Optional[datetime] = None) -> int:
        """Calculate duration in months between two dates"""
        if not start_date:
            return 0
        
        if end_date is None:
            end_date = datetime.now()
        
        if end_date < start_date:
            return 0
        
        try:
            rel_delta = relativedelta(end_date, start_date)
            months = rel_delta.years * 12 + rel_delta.months
            return max(0, months)
        except:
            return 0
    
    def calculate_years_duration(self, start_date: datetime, end_date: Optional[datetime] = None) -> float:
        """Calculate duration in years (with decimal) between two dates"""
        months = self.calculate_months_duration(start_date, end_date)
        return round(months / 12, 2)
    
    # ============================================
    # TOTAL EXPERIENCE CALCULATION
    # ============================================
    
    def extract_experience_from_text(self, text: str) -> float:
        """
        Extract total years of experience from resume text
        Handles: explicit year mentions and date ranges with intelligent parsing
        """
        if not text:
            return 0.0
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Pattern 1: Direct "X+ years" or "X years experience"
        years_pattern = r'(?:^|\s)(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)?'
        matches = re.findall(years_pattern, text, re.IGNORECASE | re.MULTILINE)
        
        if matches:
            try:
                max_years = int(max(matches, key=int))
                if max_years > 0:
                    return float(max_years)
            except:
                pass
        
        # Pattern 2: Extract YYYY - YYYY or YYYY-YYYY date ranges
        total_years = 0
        all_durations = []
        
        # Pattern for simple year ranges: "2015 - 2021", "2015-2021"
        year_range_pattern = r'(\d{4})\s*[-–—to\s]+\s*(?:present|current|ongoing|(\d{4}))'
        year_matches = re.findall(year_range_pattern, text, re.IGNORECASE)
        
        for match in year_matches:
            try:
                start_year = int(match[0])
                # match[1] is either empty (for "present") or contains end year
                end_year = int(match[1]) if match[1] else datetime.now().year
                
                duration = abs(end_year - start_year)
                if 0 < duration <= 80:  # Reasonable duration
                    all_durations.append(duration)
            except (ValueError, TypeError):
                pass
        
        # Pattern 3: Month/Date ranges like "Jan 2015 - Dec 2021"
        month_year_pattern = r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{4})\s*[-–—to\s]+\s*(?:present|current|ongoing|(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+)?(\d{4}))'
        month_matches = re.findall(month_year_pattern, text, re.IGNORECASE)
        
        for match in month_matches:
            try:
                start_year = int(match[0])
                end_year = int(match[1]) if match[1] else datetime.now().year
                
                duration = abs(end_year - start_year)
                if 0 < duration <= 80:
                    all_durations.append(duration)
            except (ValueError, TypeError):
                pass
        
        # Calculate total experience from all job entries
        if all_durations:
            # If we found multiple job periods, sum them up
            # Otherwise just return the max duration
            if len(all_durations) > 1:
                total_years = sum(all_durations)
            else:
                total_years = all_durations[0]
            
            return float(total_years)
        
        return 0.0
    
    def extract_experience_from_structured(self, experience_entries: List[Dict]) -> Tuple[float, List[Dict]]:
        """
        Calculate total experience from structured experience entries
        Returns: (total_years, enhanced_entries)
        """
        if not experience_entries:
            return 0.0, []
        
        total_months = 0
        enhanced_entries = []
        
        for entry in experience_entries:
            entry_copy = entry.copy()
            
            # Extract dates from period
            period = entry.get('period', '')
            start_date, end_date = self.extract_experience_period(period)
            
            entry_copy['start_date'] = start_date.isoformat() if start_date else None
            entry_copy['end_date'] = end_date.isoformat() if end_date else None
            
            # Calculate duration
            if start_date:
                months = self.calculate_months_duration(start_date, end_date)
                years = self.calculate_years_duration(start_date, end_date)
                entry_copy['duration_months'] = months
                entry_copy['duration_years'] = years
                total_months += months
            else:
                entry_copy['duration_months'] = 0
                entry_copy['duration_years'] = 0
            
            enhanced_entries.append(entry_copy)
        
        total_years = round(total_months / 12, 2)
        return total_years, enhanced_entries
    
    # ============================================
    # SKILL EXPERIENCE EXTRACTION
    # ============================================
    
    def extract_skill_experience(self, text: str, skill: str) -> Dict:
        """
        Extract experience related to a specific skill
        Returns: {years: float, mentions: count, context: str}
        """
        skill_lower = skill.lower()
        
        # Find all mentions of the skill
        pattern = rf'(?:^|\s)([^.]*{re.escape(skill)}[^.]*(?:\.|$))'
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        
        # Extract years from mentions
        years_found = []
        for match in matches:
            years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
            year_matches = re.findall(years_pattern, match)
            if year_matches:
                years_found.extend([int(y) for y in year_matches])
        
        return {
            'skill': skill,
            'mentions': len(matches),
            'years': max(years_found) if years_found else 0,
            'confidence': 'high' if years_found else 'medium' if matches else 'low',
            'context': matches[:2] if matches else []  # First 2 mentions
        }
    
    # ============================================
    # HIGH-LEVEL SUMMARY
    # ============================================
    
    def get_experience_summary(self, resume_data: Dict) -> Dict:
        """
        Generate comprehensive experience summary from structured resume data
        """
        summary = {
            'total_years': 0.0,
            'experience_entries': [],
            'level': 'Fresher',  # Fresher, Junior, Mid, Senior, Lead, Executive
            'industries': [],
            'job_titles': [],
            'skills_experience': {}
        }
        
        # Try Method 1: Calculate from structured experience entries
        if 'experience' in resume_data and resume_data['experience']:
            try:
                total_years, enhanced = self.extract_experience_from_structured(resume_data['experience'])
                summary['total_years'] = total_years
                summary['experience_entries'] = enhanced
                
                # Extract job titles
                summary['job_titles'] = [e.get('title', '').strip() for e in enhanced if e.get('title')]
            except Exception as e:
                print(f"Error in extract_experience_from_structured: {e}")
        
        # Fallback to Method 2: Extract years from raw text if structured didn't work well
        if summary['total_years'] == 0 and 'raw_text' in resume_data:
            try:
                summary['total_years'] = self.extract_experience_from_text(resume_data['raw_text'])
            except Exception as e:
                print(f"Error in extract_experience_from_text: {e}")
        
        # Determine experience level based on years
        years = summary['total_years']
        if years < 1:
            summary['level'] = 'Fresher'
        elif years < 3:
            summary['level'] = 'Junior'
        elif years < 7:
            summary['level'] = 'Mid'
        elif years < 12:
            summary['level'] = 'Senior'
        else:
            summary['level'] = 'Lead/Executive'
        
        # Extract skills experience if available
        if 'skills' in resume_data and resume_data['skills'] and 'raw_text' in resume_data:
            try:
                for skill in resume_data['skills'][:10]:  # Top 10 skills
                    skill_exp = self.extract_skill_experience(resume_data.get('raw_text', ''), skill)
                    if skill_exp['years'] > 0:
                        summary['skills_experience'][skill] = skill_exp['years']
            except Exception as e:
                print(f"Error extracting skill experience: {e}")
        
        return summary


# Backward compatibility wrapper functions
def extract_experience(text: str) -> int:
    """Legacy function - returns integer years"""
    extractor = ExperienceExtractor()
    years = extractor.extract_experience_from_text(text)
    return int(years)


def extract_experience_advanced(resume_data: Dict) -> Dict:
    """Extract detailed experience information from structured resume data"""
    extractor = ExperienceExtractor()
    return extractor.get_experience_summary(resume_data)
