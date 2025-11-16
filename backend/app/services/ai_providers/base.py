from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAIProvider(ABC):
    """Базовый абстрактный класс для AI-провайдеров"""

    @abstractmethod
    async def analyze_document_structure(self, text_content: str) -> Dict[str, Any]:
        """
        Анализирует структуру документа

        Args:
            text_content: Текстовое содержимое документа

        Returns:
            Словарь с результатами анализа структуры
        """
        pass

    @abstractmethod
    async def classify_paragraph(self, paragraph_text: str, context: str = "") -> Dict[str, Any]:
        """
        Классифицирует отдельный параграф

        Args:
            paragraph_text: Текст параграфа
            context: Контекст (предыдущие параграфы)

        Returns:
            Классификация параграфа
        """
        pass

    def _create_structure_prompt(self, text_content: str) -> str:
        """Создает промпт для анализа структуры документа"""
        return f"""Проанализируй структуру научного документа и определи следующие элементы:

1. Титульный лист (если есть)
2. Содержание/Оглавление
3. Введение
4. Основные главы и подразделы (определи их номера и заголовки)
5. Заключение
6. Список литературы
7. Таблицы (определи их номера и подписи)
8. Рисунки (определи их номера и подписи)

Для каждого элемента укажи:
- Тип элемента (title_page, contents, introduction, chapter, subchapter, conclusion, references, table, figure)
- Уровень заголовка (для глав и подразделов: 1, 2, 3)
- Номер элемента (если применимо)
- Текст заголовка
- Примерное положение в документе (начальная позиция текста)

Верни результат СТРОГО в формате JSON:
{{
    "elements": [
        {{
            "type": "chapter",
            "level": 1,
            "number": "1",
            "title": "Название главы",
            "position": 0,
            "text_preview": "Первые 100 символов текста..."
        }},
        ...
    ]
}}

Документ для анализа:
{text_content[:15000]}
"""

    def _create_paragraph_prompt(self, paragraph_text: str, context: str = "") -> str:
        """Создает промпт для классификации параграфа"""
        return f"""Определи тип следующего параграфа в научном документе:

Возможные типы:
- heading_1: Заголовок первого уровня (глава)
- heading_2: Заголовок второго уровня (подраздел)
- heading_3: Заголовок третьего уровня
- normal: Обычный текст
- list_item: Элемент списка
- reference: Элемент списка литературы
- table_caption: Подпись таблицы
- figure_caption: Подпись рисунка

Контекст (предыдущий текст):
{context[-500:]}

Параграф для анализа:
{paragraph_text}

Верни результат в формате JSON:
{{
    "type": "тип_параграфа",
    "confidence": 0.95,
    "is_numbered": true/false,
    "number": "1.2.3" (если применимо)
}}
"""

    def _extract_json_from_response(self, response_text: str) -> str:
        """Извлекает JSON из текстового ответа модели"""
        # Ищем JSON между ```json и ``` или просто парсим весь ответ
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            return response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            return response_text[json_start:json_end].strip()
        else:
            return response_text.strip()
