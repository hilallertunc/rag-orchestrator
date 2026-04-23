import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.services.llm_service import ask_llm
from app.services.cache_service import get_from_cache, save_to_cache
from app.services.router_service import classify_question, select_model
from app.services.rag_service import search_documents
from app.core.logger import get_logger
from app.core.database import get_db
from app.models.request_log import RequestLog

logger = get_logger(__name__)
router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    tenant: str = "free"

class DocumentRequest(BaseModel):
    text: str
    metadata: dict = {}

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

@router.post("/documents")
async def add_doc(request: DocumentRequest):
    from app.services.rag_service import add_document
    doc_id = await add_document(request.text, request.metadata)
    return {"doc_id": doc_id, "status": "added"}

@router.post("/ask", response_model=QuestionResponse)
async def ask(request: QuestionRequest, db: AsyncSession = Depends(get_db)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Soru boş olamaz")

    start_time = time.time()

    logger.info("request_received", extra={
        "extra": {"question": request.question, "tenant": request.tenant}
    })

    cached = await get_from_cache(request.question)
    if cached:
        total_ms = round((time.time() - start_time) * 1000)
        return QuestionResponse(
            question=request.question,
            answer=cached["answer"],
            model=cached["model"],
            tokens_used=0,
            duration_ms=total_ms,
            strategy="cache_hit"
        )

    
    complexity = classify_question(request.question)
    model = select_model(complexity, request.tenant)

    context = ""
    strategy = f"{complexity}_llm"

    if complexity == "complex":
        documents = await search_documents(request.question)
        if documents:
            context = "\n\n".join([doc["text"] for doc in documents])
            strategy = "rag"
            logger.info("rag_context_found", extra={
                "extra": {"doc_count": len(documents)}
            })

    result = await ask_llm(request.question, context=context, model=model)
    total_ms = round((time.time() - start_time) * 1000)

    await save_to_cache(request.question, {
        "answer": result["answer"],
        "model": model
    })

   
    log = RequestLog(
        question=request.question,
        answer=result["answer"],
        strategy=strategy,
        model=result["model"],
        tokens_used=result["tokens_used"],
        duration_ms=total_ms,
        has_context=bool(context)
    )
    db.add(log)
    await db.commit()

    logger.info("request_completed", extra={
        "extra": {
            "tokens_used": result["tokens_used"],
            "duration_ms": total_ms,
            "strategy": strategy
        }
    })

    return QuestionResponse(
        question=request.question,
        answer=result["answer"],
        model=result["model"],
        tokens_used=result["tokens_used"],
        duration_ms=total_ms,
        strategy=strategy
    )