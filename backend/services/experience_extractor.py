import re

def extract_experience(text):
    matches = re.findall(r'(\d+)\+?\s*years', text.lower())

    if matches:
        return max([int(x) for x in matches])

    return 0