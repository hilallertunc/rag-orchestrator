import time
from groq import Groq
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)
client = Groq(api_key=settings.groq_api_key)

async def ask_llm(question: str, context: str = "") -> dict:
    

    if context:
        system_prompt = f"""Sen yardımcı bir asistansın.
Aşağıdaki bilgileri kullanarak soruyu cevapla:

{context}

Eğer bilgiler soruyla ilgili değilse, genel bilginle cevap ver."""
    else:
        system_prompt = "Sen yardımcı bir asistansın. Soruları net ve kısa cevapla."

    start_time = time.time()

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        model="llama-3.3-70b-versatile",
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
            "model": "llama-3.3-70b-versatile",
            "has_context": bool(context)
        }
    })

    return {
        "answer": answer,
        "model": "llama-3.3-70b-versatile",
        "tokens_used": tokens_used,
        "duration_ms": duration_ms
    }