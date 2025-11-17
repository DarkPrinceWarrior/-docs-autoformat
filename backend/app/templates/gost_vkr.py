from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any
from app.templates.base import BaseTemplate


class GOSTVKRTemplate(BaseTemplate):
    """Шаблон форматирования выпускных квалификационных работ по ГОСТ 7.32-2017"""

    @property
    def template_name(self) -> str:
        return "gost_vkr"

    @property
    def template_description(self) -> str:
        return "Выпускная квалификационная работа (ВКР) по ГОСТ 7.32-2017"

    def apply_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
        """Применяет форматирование ГОСТ 7.32-2017 к ВКР"""

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
        """Создает стили документа по ГОСТ 7.32-2017 для ВКР"""

        # Создаем базовые стили
        self._create_base_styles(doc)

        # Стиль для заголовка 1 уровня (главы) - прописные, по центру, жирный
        self._create_heading_style(
            doc,
            'Heading 1',
            font_size=self.FONT_SIZE,
            bold=True,
            all_caps=True,
            alignment=WD_ALIGN_PARAGRAPH.CENTER,
            indent=0
        )

        # Стиль для заголовка 2 уровня (разделы) - жирный, с отступом
        self._create_heading_style(
            doc,
            'Heading 2',
            font_size=self.FONT_SIZE,
            bold=True,
            all_caps=False,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            indent=self.PARAGRAPH_INDENT
        )

        # Стиль для заголовка 3 уровня (подразделы) - жирный, с отступом
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
        """Форматирует параграфы согласно определенной структуре"""

        elements = structure.get('elements', [])

        for i, paragraph in enumerate(doc.paragraphs):
            if not paragraph.text.strip():
                continue

            # Определяем тип параграфа на основе структуры
            element_type = self._find_element_type(paragraph.text, elements, i)

            # Применяем соответствующий стиль
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
        """Определяет тип элемента по тексту и структуре"""

        # Ищем соответствие в элементах структуры
        for element in elements:
            if element.get('type') in ['chapter', 'introduction', 'conclusion']:
                if text.strip().upper().startswith(element.get('title', '').upper()[:20]):
                    level = element.get('level', 1)
                    if level == 1:
                        return 'heading_1'
                    elif level == 2:
                        return 'heading_2'
                    elif level == 3:
                        return 'heading_3'

            if element.get('type') == 'reference':
                if text.strip() and text.strip()[0].isdigit():
                    return 'reference'

        return 'normal'

    def _format_references(self, doc: Document):
        """Форматирует список литературы по ГОСТ 7.0.5-2008"""

        in_references = False

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip().upper()

            # Определяем начало списка литературы
            if 'СПИСОК' in text and ('ЛИТЕРАТУР' in text or 'ИСТОЧНИК' in text):
                in_references = True
                self._apply_paragraph_style(paragraph, 'Heading 1')
                self._remove_trailing_period(paragraph)
                continue

            # Форматируем элементы списка литературы
            if in_references:
                if paragraph.text.strip():
                    # Проверяем, начинается ли с номера
                    if paragraph.text.strip()[0].isdigit():
                        paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        paragraph.paragraph_format.first_line_indent = Cm(0)
                        paragraph.paragraph_format.left_indent = Cm(1.25)
                        paragraph.paragraph_format.hanging_indent = Cm(1.25)

                        for run in paragraph.runs:
                            run.font.name = self.FONT_NAME
                            run.font.size = Pt(self.FONT_SIZE)
