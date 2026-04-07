import re
from skills import SKILL_DB

def chunk_text(text, chunk_size=150):
    words = text.split()
    return [
        " ".join(words[i:i+chunk_size])
        for i in range(0, len(words), chunk_size)
    ]



def extract_skills(text):
    text = text.lower()

    found = []
    for skill in SKILL_DB:
        if skill in text:
            found.append(skill)

    return list(set(found))


def extract_keywords(text):
    """Alias to extract skills/keywords from JD text."""
    return extract_skills(text)