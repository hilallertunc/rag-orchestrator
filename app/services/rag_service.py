from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logger import get_logger
import uuid

logger = get_logger(__name__)

COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384

model = SentenceTransformer(EMBEDDING_MODEL)

client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key
)

async def ensure_collection():
    """Collection yoksa oluştur."""
    try:
        collections = client.get_collections().collections
        names = [c.name for c in collections]
        if COLLECTION_NAME not in names:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            logger.info("collection_created", extra={"extra": {"collection": COLLECTION_NAME}})
    except Exception as e:
        logger.error("collection_error", extra={"extra": {"error": str(e)}})

async def add_document(text: str, metadata: dict = {}) -> str:
    """Döküman ekle."""
    await ensure_collection()
    
    embedding = model.encode(text).tolist()
    doc_id = str(uuid.uuid4())
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=doc_id,
                vector=embedding,
                payload={"text": text, **metadata}
            )
        ]
    )
    
    logger.info("document_added", extra={"extra": {"doc_id": doc_id}})
    return doc_id

async def search_documents(query: str, limit: int = 3) -> list[dict]:
    """Soruya en benzer dökümanları bul."""
    try:
        await ensure_collection()
        
        query_embedding = model.encode(query).tolist()
        
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=0.5
        )
        
        documents = []
        for result in results:
            documents.append({
                "text": result.payload.get("text", ""),
                "score": result.score,
                "id": result.id
            })
        
        logger.info("documents_searched", extra={
            "extra": {
                "query": query,
                "found": len(documents)
            }
        })
        
        return documents
    except Exception as e:
        logger.error("search_error", extra={"extra": {"error": str(e)}})
        return []