from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DocumentStatus(str, enum.Enum):
    """Статусы обработки документа"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """Модель документа"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    original_file_path = Column(String(500), nullable=False)
    formatted_file_path = Column(String(500), nullable=True)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    structure_analysis = Column(Text, nullable=True)  # JSON с результатами анализа
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.original_filename}, status={self.status})>"
