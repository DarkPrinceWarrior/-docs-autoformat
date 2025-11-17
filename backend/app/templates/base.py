from abc import ABC, abstractmethod
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from typing import Dict, Any


class BaseTemplate(ABC):
    """Базовый абстрактный класс для шаблонов форматирования документов"""

    # Базовые константы, которые могут быть переопределены в наследниках
    FONT_NAME = "Times New Roman"
    FONT_SIZE = 14
    LINE_SPACING = 1.5
    PARAGRAPH_INDENT = 1.25  # см

    # Поля страницы (см)
    MARGIN_TOP = 2.0
    MARGIN_BOTTOM = 2.0
    MARGIN_LEFT = 3.0
    MARGIN_RIGHT = 1.0

    @property
    @abstractmethod
    def template_name(self) -> str:
        """Название шаблона"""
        pass

    @property
    @abstractmethod
    def template_description(self) -> str:
        """Описание шаблона"""
        pass

    @abstractmethod
    def apply_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
        """
        Применяет форматирование к документу

        Args:
            doc: Объект документа python-docx
            structure: Структура документа из AI анализа

        Returns:
            Отформатированный документ
        """
        pass

    def _apply_page_settings(self, doc: Document):
        """Применяет настройки полей страницы"""
        sections = doc.sections
        for section in sections:
            section.top_margin = Cm(self.MARGIN_TOP)
            section.bottom_margin = Cm(self.MARGIN_BOTTOM)
            section.left_margin = Cm(self.MARGIN_LEFT)
            section.right_margin = Cm(self.MARGIN_RIGHT)

    def _create_base_styles(self, doc: Document):
        """Создает базовые стили документа"""
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

    def _create_heading_style(
        self,
        doc: Document,
        style_name: str,
        font_size: int = None,
        bold: bool = True,
        all_caps: bool = False,
        alignment: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.LEFT,
        indent: float = None
    ):
        """
        Создает стиль заголовка

        Args:
            doc: Документ
            style_name: Имя стиля
            font_size: Размер шрифта (если None, используется FONT_SIZE)
            bold: Жирный шрифт
            all_caps: Все заглавные
            alignment: Выравнивание
            indent: Отступ первой строки в см (если None, используется PARAGRAPH_INDENT)
        """
        styles = doc.styles

        try:
            heading_style = styles[style_name]
        except KeyError:
            heading_style = styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)

        heading_font = heading_style.font
        heading_font.name = self.FONT_NAME
        heading_font.size = Pt(font_size if font_size else self.FONT_SIZE)
        heading_font.bold = bold
        heading_font.all_caps = all_caps

        heading_paragraph = heading_style.paragraph_format
        heading_paragraph.alignment = alignment
        heading_paragraph.space_before = Pt(0)
        heading_paragraph.space_after = Pt(0)
        heading_paragraph.first_line_indent = Cm(indent if indent is not None else self.PARAGRAPH_INDENT)

    def _apply_paragraph_style(self, paragraph, style_name: str):
        """Применяет стиль к параграфу"""
        paragraph.style = style_name

        # Применяем базовые настройки шрифта
        for run in paragraph.runs:
            run.font.name = self.FONT_NAME
            run.font.size = Pt(self.FONT_SIZE)

    def _remove_trailing_period(self, paragraph):
        """Удаляет точку в конце заголовка"""
        if paragraph.text.endswith('.'):
            paragraph.text = paragraph.text[:-1]

    def get_template_info(self) -> Dict[str, str]:
        """Возвращает информацию о шаблоне"""
        return {
            "name": self.template_name,
            "description": self.template_description,
            "font": self.FONT_NAME,
            "font_size": str(self.FONT_SIZE),
            "line_spacing": str(self.LINE_SPACING),
        }
