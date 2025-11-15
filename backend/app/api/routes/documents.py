from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.tasks.document_tasks import process_document_task
from app.core.config import settings
from typing import List
from pydantic import BaseModel
import os
import shutil
import uuid

router = APIRouter()


class DocumentResponse(BaseModel):
    """Модель ответа с информацией о документе"""
    id: int
    original_filename: str
    status: str
    created_at: str
    structure_analysis: str | None = None
    error_message: str | None = None

    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    """Модель ответа со статусом задачи"""
    task_id: str
    status: str
    document_id: int | None = None


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузка документа для обработки

    - **file**: DOCX файл для обработки
    """

    # Проверяем расширение файла
    if not file.filename.endswith('.docx'):
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только файлы формата .docx"
        )

    # Проверяем размер файла
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Размер файла превышает максимально допустимый ({settings.MAX_FILE_SIZE / 1024 / 1024} МБ)"
        )

    # Создаем директорию для загрузок, если её нет
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Генерируем уникальное имя файла
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при сохранении файла: {str(e)}"
        )

    # Создаем запись в базе данных
    document = Document(
        original_filename=file.filename,
        original_file_path=file_path,
        status=DocumentStatus.UPLOADED
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Запускаем задачу обработки
    task = process_document_task.delay(document.id)

    return DocumentResponse(
        id=document.id,
        original_filename=document.original_filename,
        status=document.status.value,
        created_at=str(document.created_at),
        structure_analysis=document.structure_analysis,
        error_message=document.error_message
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document_status(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение статуса обработки документа

    - **document_id**: ID документа
    """

    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")

    return DocumentResponse(
        id=document.id,
        original_filename=document.original_filename,
        status=document.status.value,
        created_at=str(document.created_at),
        structure_analysis=document.structure_analysis,
        error_message=document.error_message
    )


@router.get("/documents/{document_id}/download")
async def download_formatted_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Скачивание отформатированного документа

    - **document_id**: ID документа
    """

    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")

    if document.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Документ еще не обработан. Текущий статус: {document.status.value}"
        )

    if not document.formatted_file_path or not os.path.exists(document.formatted_file_path):
        raise HTTPException(
            status_code=404,
            detail="Отформатированный файл не найден"
        )

    filename = f"formatted_{document.original_filename}"
    return FileResponse(
        path=document.formatted_file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех документов

    - **skip**: Количество пропускаемых записей
    - **limit**: Максимальное количество возвращаемых записей
    """

    result = await db.execute(
        select(Document)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()

    return [
        DocumentResponse(
            id=doc.id,
            original_filename=doc.original_filename,
            status=doc.status.value,
            created_at=str(doc.created_at),
            structure_analysis=doc.structure_analysis,
            error_message=doc.error_message
        )
        for doc in documents
    ]
