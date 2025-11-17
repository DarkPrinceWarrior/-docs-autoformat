"""GOST template for practice report documents."""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any

from .base import BaseTemplate


class GOSTPracticeReportTemplate(BaseTemplate):
    """
    Template for practice report documents.

    Key features:
    - Standard GOST formatting
    - Normal case headings
    - Standard margins like coursework
    - Specific sections for practice reports
    """

    # Similar to coursework
    MARGIN_RIGHT = 1.5

    @property
    def template_name(self) -> str:
        """Template identifier."""
        return "gost_practice_report"

    @property
    def template_description(self) -> str:
        """Human-readable template description."""
        return "ГОСТ Отчёт по практике"

    def _create_document_styles(self, doc: Document):
        """Create document-specific styles."""
        # Heading 1 - main sections (numbered)
        self._create_heading_style(
            doc, 'Heading 1',
            font_size=self.FONT_SIZE,
            bold=True,
            all_caps=False,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            indent=0
        )

        # Heading 2 - subsections
        self._create_heading_style(
            doc, 'Heading 2',
            font_size=self.FONT_SIZE,
            bold=True,
            all_caps=False,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            indent=0
        )

        # Heading 3
        self._create_heading_style(
            doc, 'Heading 3',
            font_size=self.FONT_SIZE,
            bold=False,
            all_caps=False,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            indent=0
        )

    def apply_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
        """
        Apply practice report formatting to the document.

        Args:
            doc: Document to format
            structure: Document structure from AI analysis

        Returns:
            Formatted document
        """
        # Apply base formatting
        self._apply_page_settings(doc)
        self._create_base_styles(doc)
        self._create_document_styles(doc)

        # Process document sections
        if 'sections' in structure:
            for section in structure['sections']:
                self._format_section(doc, section)

        # Add practice-specific sections if not present
        self._ensure_practice_sections(doc, structure)

        return doc

    def _ensure_practice_sections(self, doc: Document, structure: Dict[str, Any]):
        """
        Ensure practice report has required sections.

        Typical sections:
        - Введение
        - Характеристика организации
        - Описание выполненной работы
        - Заключение
        - Список использованных источников
        """
        # This is a placeholder - in production, would check for required sections
        pass

    def _format_section(self, doc: Document, section: Dict[str, Any]):
        """Format a single section."""
        # Add heading
        heading = doc.add_heading(section.get('title', ''), level=section.get('level', 1))

        # Add content paragraphs
        if 'content' in section:
            for content_item in section['content']:
                if content_item.get('type') == 'paragraph':
                    para = doc.add_paragraph(content_item.get('text', ''))

        # Process subsections recursively
        if 'subsections' in section:
            for subsection in section['subsections']:
                self._format_section(doc, subsection)
