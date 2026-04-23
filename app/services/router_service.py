from app.core.logger import get_logger

logger = get_logger(__name__)

SIMPLE_KEYWORDS = [
    "nedir", "ne demek", "tanımla", "açıkla", "kim",
    "what is", "define", "explain", "who is", "meaning of"
]

COMPLEX_KEYWORDS = [
    "karşılaştır", "analiz et", "farkı nedir", "nasıl çalışır",
    "neden", "avantaj", "dezavantaj", "örnek ver", "kodla",
    "compare", "analyze", "difference", "how does", "why", "implement"
]

def classify_question(question: str) -> str:
    
    question_lower = question.lower()
    
    complex_score = sum(1 for kw in COMPLEX_KEYWORDS if kw in question_lower)
    simple_score = sum(1 for kw in SIMPLE_KEYWORDS if kw in question_lower)
    
    word_count = len(question.split())
    if word_count > 10:
        complex_score += 2
    elif word_count < 5:
        simple_score += 1

    if complex_score >= simple_score and complex_score > 0:
        complexity = "complex"
    else:
        complexity = "simple"

    logger.info("question_classified", extra={
        "extra": {
            "question": question,
            "complexity": complexity,
            "complex_score": complex_score,
            "simple_score": simple_score,
            "word_count": word_count
        }
    })

    return complexity


def select_model(complexity: str, tenant: str = "free") -> str:
    
    if tenant == "premium":
        return "llama-3.3-70b-versatile"
    
    if complexity == "simple":
        return "llama-3.1-8b-instant"
    else:
        return "llama-3.3-70b-versatile"