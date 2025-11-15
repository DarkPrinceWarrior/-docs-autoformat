from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from typing import Dict, Any


class GOSTFormatter:
    """Применение форматирования по ГОСТ 7.32-2017"""

    # Константы ГОСТ
    FONT_NAME = "Times New Roman"
    FONT_SIZE = 14
    LINE_SPACING = 1.5
    PARAGRAPH_INDENT = 1.25  # см

    # Поля страницы (см)
    MARGIN_TOP = 2.0
    MARGIN_BOTTOM = 2.0
    MARGIN_LEFT = 3.0
    MARGIN_RIGHT = 1.0

    def __init__(self):
        pass

    def apply_gost_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
        """
        Применяет форматирование ГОСТ к документу

        Args:
            doc: Объект документа python-docx
            structure: Структура документа из Claude анализа

        Returns:
            Отформатированный документ
        """

        # Применяем настройки страницы
        self._apply_page_settings(doc)

        # Создаем/обновляем стили
        self._create_gost_styles(doc)

        # Применяем форматирование к параграфам
        self._format_paragraphs(doc, structure)

        return doc

    def _apply_page_settings(self, doc: Document):
        """Применяет настройки полей страницы по ГОСТ"""

        sections = doc.sections
        for section in sections:
            section.top_margin = Cm(self.MARGIN_TOP)
            section.bottom_margin = Cm(self.MARGIN_BOTTOM)
            section.left_margin = Cm(self.MARGIN_LEFT)
            section.right_margin = Cm(self.MARGIN_RIGHT)

    def _create_gost_styles(self, doc: Document):
        """Создает стили по ГОСТ"""

        styles = doc.styles

        # Стиль для обычного текста
        try:
            normal_style = styles['Normal']
        except KeyError:
            normal_style = styles.add_style('Normal', WD_STYLE_TYPE.PARAGRAPH)

        normal_font = normal_style.font
        normal_font.name = self.FONT_NAME
        normal_font.size = Pt(self.FONT_SIZE)

        normal_paragraph = normal_style.paragraph_format
        normal_paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        normal_paragraph.first_line_indent = Cm(self.PARAGRAPH_INDENT)
        normal_paragraph.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        normal_paragraph.space_before = Pt(0)
        normal_paragraph.space_after = Pt(0)

        # Стиль для заголовка 1 уровня
        try:
            heading1_style = styles['Heading 1']
        except KeyError:
            heading1_style = styles.add_style('Heading 1', WD_STYLE_TYPE.PARAGRAPH)

        heading1_font = heading1_style.font
        heading1_font.name = self.FONT_NAME
        heading1_font.size = Pt(self.FONT_SIZE)
        heading1_font.bold = True
        heading1_font.all_caps = True

        heading1_paragraph = heading1_style.paragraph_format
        heading1_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading1_paragraph.space_before = Pt(0)
        heading1_paragraph.space_after = Pt(0)
        heading1_paragraph.first_line_indent = Cm(0)

        # Стиль для заголовка 2 уровня
        try:
            heading2_style = styles['Heading 2']
        except KeyError:
            heading2_style = styles.add_style('Heading 2', WD_STYLE_TYPE.PARAGRAPH)

        heading2_font = heading2_style.font
        heading2_font.name = self.FONT_NAME
        heading2_font.size = Pt(self.FONT_SIZE)
        heading2_font.bold = True

        heading2_paragraph = heading2_style.paragraph_format
        heading2_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        heading2_paragraph.space_before = Pt(0)
        heading2_paragraph.space_after = Pt(0)
        heading2_paragraph.first_line_indent = Cm(self.PARAGRAPH_INDENT)

        # Стиль для заголовка 3 уровня
        try:
            heading3_style = styles['Heading 3']
        except KeyError:
            heading3_style = styles.add_style('Heading 3', WD_STYLE_TYPE.PARAGRAPH)

        heading3_font = heading3_style.font
        heading3_font.name = self.FONT_NAME
        heading3_font.size = Pt(self.FONT_SIZE)
        heading3_font.bold = True

        heading3_paragraph = heading3_style.paragraph_format
        heading3_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        heading3_paragraph.space_before = Pt(0)
        heading3_paragraph.space_after = Pt(0)
        heading3_paragraph.first_line_indent = Cm(self.PARAGRAPH_INDENT)

    def _format_paragraphs(self, doc: Document, structure: Dict[str, Any]):
        """Форматирует параграфы согласно определенной структуре"""

        elements = structure.get('elements', [])

        for i, paragraph in enumerate(doc.paragraphs):
            if not paragraph.text.strip():
                continue

            # Определяем тип параграфа на основе структуры
            element_type = self._find_element_type(paragraph.text, elements, i)

            # Применяем соответствующий стиль
            self._apply_paragraph_style(paragraph, element_type)

    def _find_element_type(self, text: str, elements: list, index: int) -> str:
        """Определяет тип элемента по тексту и структуре"""

        # Ищем соответствие в элементах структуры
        for element in elements:
            if element.get('type') in ['chapter', 'introduction', 'conclusion']:
                if text.strip().upper().startswith(element.get('title', '').upper()[:20]):
                    if element.get('level') == 1:
                        return 'heading_1'
                    elif element.get('level') == 2:
                        return 'heading_2'
                    elif element.get('level') == 3:
                        return 'heading_3'

            if element.get('type') == 'reference':
                if text.strip().startswith(('1.', '[1]', '1)')):
                    return 'reference'

        return 'normal'

    def _apply_paragraph_style(self, paragraph, element_type: str):
        """Применяет стиль к параграфу"""

        if element_type == 'heading_1':
            paragraph.style = 'Heading 1'
            # Убираем точку в конце заголовка
            if paragraph.text.endswith('.'):
                paragraph.text = paragraph.text[:-1]

        elif element_type == 'heading_2':
            paragraph.style = 'Heading 2'
            if paragraph.text.endswith('.'):
                paragraph.text = paragraph.text[:-1]

        elif element_type == 'heading_3':
            paragraph.style = 'Heading 3'
            if paragraph.text.endswith('.'):
                paragraph.text = paragraph.text[:-1]

        else:
            paragraph.style = 'Normal'

        # Применяем базовые настройки шрифта
        for run in paragraph.runs:
            run.font.name = self.FONT_NAME
            run.font.size = Pt(self.FONT_SIZE)

    def format_references(self, doc: Document) -> Document:
        """Форматирует список литературы по ГОСТ 7.0.5-2008"""

        in_references = False

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip().upper()

            # Определяем начало списка литературы
            if 'СПИСОК' in text and ('ЛИТЕРАТУР' in text or 'ИСТОЧНИК' in text):
                in_references = True
                paragraph.style = 'Heading 1'
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

        return doc
