import time
from groq import Groq
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)
client = Groq(api_key=settings.groq_api_key)

async def ask_llm(question: str, context: str = "", model: str = "llama-3.3-70b-versatile") -> dict:
    if context:
        system_prompt = f"""You are a helpful assistant.
Use the following information to answer the question:

{context}

If the information is not relevant to the question, answer using your general knowledge."""
    else:
        system_prompt = "You are a helpful assistant. Answer questions clearly and concisely."

    start_time = time.time()

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        model=model,
        temperature=0.7,
        max_tokens=1024,
    )

    duration_ms = round((time.time() - start_time) * 1000)
    answer = chat_completion.choices[0].message.content
    tokens_used = chat_completion.usage.total_tokens

    logger.info("llm_call", extra={
        "extra": {
            "question_length": len(question),
            "tokens_used": tokens_used,
            "duration_ms": duration_ms,
            "model": model,
            "has_context": bool(context)
        }
    })

    return {
        "answer": answer,
        "model": model,
        "tokens_used": tokens_used,
        "duration_ms": duration_ms
    }