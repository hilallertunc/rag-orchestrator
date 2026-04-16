import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.services.llm_service import ask_llm
from app.core.logger import get_logger
from app.core.database import get_db
from app.models.request_log import RequestLog

logger = get_logger(__name__)
router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    question: str
    answer: str
    model: str
    tokens_used: int
    duration_ms: int
    strategy: str

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "RAG Orchestrator çalışıyor"}

@router.post("/ask", response_model=QuestionResponse)
async def ask(request: QuestionRequest, db: AsyncSession = Depends(get_db)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Soru boş olamaz")

    logger.info("request_received", extra={
        "extra": {"question": request.question}
    })

    start_time = time.time()
    result = await ask_llm(request.question)
    total_ms = round((time.time() - start_time) * 1000)

    log = RequestLog(
        question=request.question,
        answer=result["answer"],
        strategy="direct_llm",
        model=result["model"],
        tokens_used=result["tokens_used"],
        duration_ms=total_ms,
        has_context=False
    )
    db.add(log)
    await db.commit()

    logger.info("request_completed", extra={
        "extra": {
            "tokens_used": result["tokens_used"],
            "duration_ms": total_ms,
            "strategy": "direct_llm"
        }
    })

    return QuestionResponse(
        question=request.question,
        answer=result["answer"],
        model=result["model"],
        tokens_used=result["tokens_used"],
        duration_ms=total_ms,
        strategy="direct_llm"
    )