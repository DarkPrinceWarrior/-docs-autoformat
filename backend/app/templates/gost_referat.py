"""GOST template for referat (abstract) documents."""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any

from .base import BaseTemplate


class GOSTReferatTemplate(BaseTemplate):
    """
    Template for referat (abstract) documents according to GOST 7.9-95.

    Key features:
    - Smaller font size (12pt for abstracts)
    - Single line spacing for compact format
    - Normal case headings
    - Narrower margins
    - Compact structure
    """

    # Override constants for referat
    FONT_SIZE = 12  # Smaller font for abstracts
    LINE_SPACING = 1.0  # Single spacing for compact format
    PARAGRAPH_INDENT = 1.0  # Smaller indent

    # Narrower margins for referat
    MARGIN_LEFT = 2.5
    MARGIN_RIGHT = 1.5
    MARGIN_TOP = 2.0
    MARGIN_BOTTOM = 2.0

    @property
    def template_name(self) -> str:
        """Template identifier."""
        return "gost_referat"

    @property
    def template_description(self) -> str:
        """Human-readable template description."""
        return "ГОСТ Реферат (ГОСТ 7.9-95)"

    def _create_document_styles(self, doc: Document):
        """Create document-specific styles."""
        # Heading 1 - main sections
        self._create_heading_style(
            doc, 'Heading 1',
            font_size=self.FONT_SIZE,
            bold=True,
            all_caps=False,  # Normal case for referat
            alignment=WD_ALIGN_PARAGRAPH.LEFT,  # Left alignment
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

        # Heading 3 - minor subsections
        self._create_heading_style(
            doc, 'Heading 3',
            font_size=self.FONT_SIZE,
            bold=False,  # Not bold for level 3
            all_caps=False,
            alignment=WD_ALIGN_PARAGRAPH.LEFT,
            indent=0
        )

    def apply_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
        """
        Apply referat formatting to the document.

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

        # Add metadata fields (specific to referat)
        self._add_referat_metadata(doc, structure)

        # Process document sections
        if 'sections' in structure:
            for section in structure['sections']:
                self._format_section(doc, section)

        return doc

    def _add_referat_metadata(self, doc: Document, structure: Dict[str, Any]):
        """
        Add referat-specific metadata section.

        Referat typically includes:
        - UDC code
        - Keywords
        - Abstract
        """
        # Add UDC placeholder if not present
        metadata_section = doc.add_paragraph()
        metadata_section.add_run("УДК: _________").font.size = Pt(self.FONT_SIZE)
        metadata_section.paragraph_format.space_after = Pt(12)

        # Extract keywords if present
        if 'keywords' in structure:
            keywords_para = doc.add_paragraph()
            keywords_run = keywords_para.add_run(f"Ключевые слова: {', '.join(structure['keywords'])}")
            keywords_run.font.size = Pt(self.FONT_SIZE)
            keywords_run.font.bold = True
            keywords_para.paragraph_format.space_after = Pt(12)

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
