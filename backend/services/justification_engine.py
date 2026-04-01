def generate_justification(result, jd_text):
    skills = result["matched_skills"]
    years = result["experience"]
    similarity = result["similarity"]

    lines = []

    if skills:
        lines.append(f"Matches key skills: {', '.join(skills[:3])}")

    if years >= 5:
        lines.append("Strong industry experience")
    elif years >= 2:
        lines.append("Moderate experience")
    else:
        lines.append("Entry-level profile")

    if similarity > 0.75:
        lines.append("Highly aligned with job requirements")
    elif similarity > 0.5:
        lines.append("Partially aligned with job requirements")

    return ". ".join(lines) + "."
def detect_hidden_gem(similarity, skill_score):
    if similarity > 0.7 and skill_score < 0.3:
        return True
    return False