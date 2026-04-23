from app.services.llm_service import ask_llm
from app.services.eval_service import evaluate_response
from app.core.logger import get_logger

logger = get_logger(__name__)

TEST_CASES = [
    {
        "question": "What is Python?",
        "expected_keywords": ["programming", "language", "code"]
    },
    {
        "question": "What is RAG in AI?",
        "expected_keywords": ["retrieval", "generation", "document"]
    },
    {
        "question": "How does caching work?",
        "expected_keywords": ["store", "memory", "speed", "cache"]
    }
]

async def run_eval() -> dict:
    results = []

    for case in TEST_CASES:
        result = await ask_llm(case["question"])
        answer = result["answer"]

        eval_result = evaluate_response(case["question"], answer)

        keyword_hits = sum(
            1 for kw in case["expected_keywords"]
            if kw.lower() in answer.lower()
        )
        keyword_score = round((keyword_hits / len(case["expected_keywords"])) * 100)

        results.append({
            "question": case["question"],
            "score": eval_result["score"],
            "keyword_score": keyword_score,
            "issues": eval_result["issues"],
            "passed": eval_result["passed"]
        })

        logger.info("eval_case_completed", extra={
            "extra": {
                "question": case["question"],
                "score": eval_result["score"],
                "passed": eval_result["passed"]
            }
        })

    passed = sum(1 for r in results if r["passed"])
    avg_score = round(sum(r["score"] for r in results) / len(results), 2)

    return {
        "total_cases": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "avg_score": avg_score,
        "results": results
    }