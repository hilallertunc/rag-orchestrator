UNCERTAINTY_PHRASES = [
    "i don't know", "i'm not sure", "bilmiyorum", "emin değilim",
    "maalesef", "unfortunately", "cannot answer", "cevap veremiyorum"
]

def evaluate_response(question: str, answer: str) -> dict:
    issues = []
    score = 100

    if len(answer.strip()) < 30:
        issues.append("answer_too_short")
        score -= 40

    if len(answer.strip()) < 10:
        issues.append("answer_empty")
        score -= 40

    answer_lower = answer.lower()
    for phrase in UNCERTAINTY_PHRASES:
        if phrase in answer_lower:
            issues.append("uncertainty_detected")
            score -= 20
            break

    question_words = set(question.lower().split())
    answer_words = set(answer.lower().split())
    overlap = question_words & answer_words
    if len(overlap) < 1:
        issues.append("low_relevance")
        score -= 20

    return {
        "score": max(score, 0),
        "issues": issues,
        "passed": score >= 60
    }