def experience_weight(years):
    if years >= 5:
        return 1.0
    elif years >= 2:
        return 0.7
    else:
        return 0.4

def calculate_score(similarity, years, skill_score):
    return (similarity * 0.6) + (experience_weight(years) * 0.25) + (skill_score * 0.15)