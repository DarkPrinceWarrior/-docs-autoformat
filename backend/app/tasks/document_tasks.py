from celery import Task
from app.tasks.celery_app import celery_app
from app.services.docx_processor import DocxProcessor
from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentStatus
from sqlalchemy import select
import asyncio
import json


class DatabaseTask(Task):
    """Базовая задача с поддержкой асинхронной работы с БД"""
    pass


@celery_app.task(bind=True, base=DatabaseTask, name="process_document")
def process_document_task(self, document_id: int):
    """
    Celery задача для обработки документа

    Args:
        document_id: ID документа в базе данных
    """

    async def async_process():
        async with AsyncSessionLocal() as session:
            try:
                # Получаем документ из БД
                result = await session.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()

                if not document:
                    raise ValueError(f"Документ с ID {document_id} не найден")

                # Обновляем статус на "в обработке"
                document.status = DocumentStatus.PROCESSING
                await session.commit()

                # Создаем процессор с указанным шаблоном
                processor = DocxProcessor(template_name=document.template_name)

                # Обрабатываем документ
                output_path, structure = await processor.process_document(
                    input_path=document.original_file_path,
                    output_path=document.original_file_path.replace('.docx', '_formatted.docx')
                )

                # Обновляем документ в БД
                document.formatted_file_path = output_path
                document.structure_analysis = json.dumps(structure, ensure_ascii=False)
                document.status = DocumentStatus.COMPLETED
                await session.commit()

                return {
                    "status": "success",
                    "document_id": document_id,
                    "output_path": output_path
                }

            except Exception as e:
                # В случае ошибки обновляем статус
                if document:
                    document.status = DocumentStatus.FAILED
                    document.error_message = str(e)
                    await session.commit()

                raise

    # Запускаем асинхронную обработку
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Если цикл уже запущен, создаем новый
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(async_process())
