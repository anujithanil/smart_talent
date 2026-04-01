import re

def chunk_text(text, chunk_size=150):
    words = text.split()
    return [
        " ".join(words[i:i+chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


def extract_keywords(text):
    words = re.findall(r'\b[A-Za-z\+\#\.]{2,}\b', text)
    return list(set([w.lower() for w in words]))[:30]