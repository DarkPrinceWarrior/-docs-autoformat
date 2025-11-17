from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any
from app.templates.base import BaseTemplate


class GOSTCourseworkTemplate(BaseTemplate):
    """Шаблон форматирования курсовых работ по ГОСТ"""

    # Поля для курсовой работы (могут отличаться от ВКР)
    MARGIN_TOP = 2.0
    MARGIN_BOTTOM = 2.0
    MARGIN_LEFT = 3.0
    MARGIN_RIGHT = 1.5  # Немного шире правое поле

    @property
    def template_name(self) -> str:
        return "gost_coursework"

    @property
    def template_description(self) -> str:
        return "Курсовая работа по ГОСТ (упрощенный вариант)"

    def apply_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
        """Применяет форматирование ГОСТ к курсовой работе"""

        # Применяем настройки страницы
        self._apply_page_settings(doc)

        # Создаем стили
        self._create_document_styles(doc)

        # Применяем форматирование к параграфам
        self._format_paragraphs(doc, structure)

        # Форматируем список литературы
        self._format_references(doc)

        return doc

    def _create_document_styles(self, doc: Document):
        """Создает стили документа для курсовой работы"""

        # Создаем базовые стили
        self._create_base_styles(doc)

        # Стиль для заголовка 1 уровня - жирный, по центру, обычный регистр
        # (для курсовых не всегда требуются прописные буквы)
        self._create_heading_style(
            doc,
            'Heading 1',
            font_size=self.FONT_SIZE,
            bold=True,
            all_caps=False,  # Обычный регистр для курсовых
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
            indent=0
        )

        # Стиль для заголовка 2 уровня - жирный, с отступом
        self._create_heading_style(
            doc,
            'Heading 2',
            font_size=self.FONT_SIZE,
            bold=True,
            all_caps=False,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            indent=self.PARAGRAPH_INDENT
        )

        # Стиль для заголовка 3 уровня - жирный, с отступом
        self._create_heading_style(
            doc,
            'Heading 3',
            font_size=self.FONT_SIZE,
            bold=True,
            all_caps=False,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            indent=self.PARAGRAPH_INDENT
        )

    def _format_paragraphs(self, doc: Document, structure: Dict[str, Any]):
        """Форматирует параграфы курсовой работы"""

        elements = structure.get('elements', [])

        for i, paragraph in enumerate(doc.paragraphs):
            if not paragraph.text.strip():
                continue

            # Определяем тип параграфа
            element_type = self._find_element_type(paragraph.text, elements, i)

            # Применяем стиль
            if element_type == 'heading_1':
                self._apply_paragraph_style(paragraph, 'Heading 1')
                self._remove_trailing_period(paragraph)

            elif element_type == 'heading_2':
                self._apply_paragraph_style(paragraph, 'Heading 2')
                self._remove_trailing_period(paragraph)

            elif element_type == 'heading_3':
                self._apply_paragraph_style(paragraph, 'Heading 3')
                self._remove_trailing_period(paragraph)

            else:
                self._apply_paragraph_style(paragraph, 'Normal')

    def _find_element_type(self, text: str, elements: list, index: int) -> str:
        """Определяет тип элемента для курсовой работы"""

        text_upper = text.strip().upper()

        # Специфичные для курсовой работы разделы
        coursework_sections = [
            'ВВЕДЕНИЕ',
            'ЗАКЛЮЧЕНИЕ',
            'ВЫВОДЫ',
            'СПИСОК ЛИТЕРАТУРЫ',
            'СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ',
            'ПРИЛОЖЕНИЕ',
        ]

        # Проверяем на основные разделы курсовой
        for section in coursework_sections:
            if text_upper.startswith(section):
                return 'heading_1'

        # Проверяем по структуре из AI анализа
        for element in elements:
            if element.get('type') in ['chapter', 'introduction', 'conclusion']:
                if text_upper.startswith(element.get('title', '').upper()[:20]):
                    level = element.get('level', 1)
                    if level == 1:
                        return 'heading_1'
                    elif level == 2:
                        return 'heading_2'
                    elif level == 3:
                        return 'heading_3'

            # Проверяем нумерованные заголовки (например, "1. Название" или "1.1 Название")
            if text.strip() and (text.strip()[0].isdigit() or 'ГЛАВА' in text_upper):
                # Определяем уровень по количеству точек в номере
                parts = text.split()
                if parts:
                    first_part = parts[0].rstrip('.')
                    if first_part.replace('.', '').isdigit():
                        dots_count = first_part.count('.')
                        if dots_count == 0:
                            return 'heading_1'
                        elif dots_count == 1:
                            return 'heading_2'
                        elif dots_count >= 2:
                            return 'heading_3'

        return 'normal'

    def _format_references(self, doc: Document):
        """Форматирует список литературы курсовой работы"""

        in_references = False

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip().upper()

            # Определяем начало списка литературы
            if ('СПИСОК' in text and ('ЛИТЕРАТУР' in text or 'ИСТОЧНИК' in text)) or \
               'БИБЛИОГРАФИЧЕСКИЙ СПИСОК' in text:
                in_references = True
                self._apply_paragraph_style(paragraph, 'Heading 1')
                self._remove_trailing_period(paragraph)
                continue

            # Форматируем элементы списка
            if in_references:
                if paragraph.text.strip():
                    # Проверяем формат нумерации (1., [1], 1))
                    first_char = paragraph.text.strip()[0]
                    if first_char.isdigit() or first_char == '[':
                        paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        paragraph.paragraph_format.first_line_indent = Cm(0)
                        paragraph.paragraph_format.left_indent = Cm(1.0)
                        paragraph.paragraph_format.hanging_indent = Cm(1.0)

                        for run in paragraph.runs:
                            run.font.name = self.FONT_NAME
                            run.font.size = Pt(self.FONT_SIZE)
