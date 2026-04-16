from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    strategy = Column(String, nullable=False)
    model = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    has_context = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)