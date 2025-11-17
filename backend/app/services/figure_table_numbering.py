"""Figure and table numbering for GOST documents."""
from typing import List, Dict, Any, Tuple
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.table import Table
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.oxml import parse_xml
import re


class FigureTableNumbering:
    """Handles numbering of figures and tables according to GOST."""

    FONT_NAME = "Times New Roman"
    FONT_SIZE = 14

    def __init__(self, template_name: str = 'gost_vkr'):
        """
        Initialize figure/table numbering.

        Args:
            template_name: Name of the GOST template
        """
        self.template_name = template_name

    def number_tables(
        self,
        doc: Document,
        numbering_style: str = 'continuous'
    ) -> Dict[str, Any]:
        """
        Number tables in document.

        Args:
            doc: Document to process
            numbering_style: 'continuous' (1, 2, 3...) or 'by_section' (1.1, 1.2, 2.1...)

        Returns:
            Dictionary with numbering results
        """
        tables_info = []
        table_counter = 0
        current_section = 1

        for i, element in enumerate(doc.element.body):
            # Check if this is a table
            if isinstance(element, CT_Tbl):
                table = Table(element, doc)
                table_counter += 1

                # Determine table number
                if numbering_style == 'by_section':
                    table_num = f"{current_section}.{table_counter}"
                else:
                    table_num = str(table_counter)

                # Find or create caption
                caption = self._find_table_caption(doc, i, element)

                if caption:
                    # Update existing caption
                    self._format_table_caption(caption, table_num)
                else:
                    # Create new caption
                    caption = self._create_table_caption(doc, element, table_num)

                tables_info.append({
                    'number': table_num,
                    'caption': caption.text if caption else None,
                    'rows': len(table.rows),
                    'cols': len(table.columns)
                })

            # Track section changes for by_section numbering
            elif isinstance(element, CT_P):
                para = doc.paragraphs[self._get_paragraph_index(doc, element)]
                if para.style.name == 'Heading 1':
                    if numbering_style == 'by_section':
                        current_section += 1
                        table_counter = 0

        return {
            'total_tables': len(tables_info),
            'numbering_style': numbering_style,
            'tables': tables_info
        }

    def number_figures(
        self,
        doc: Document,
        numbering_style: str = 'continuous'
    ) -> Dict[str, Any]:
        """
        Number figures/images in document.

        Args:
            doc: Document to process
            numbering_style: 'continuous' or 'by_section'

        Returns:
            Dictionary with numbering results
        """
        figures_info = []
        figure_counter = 0
        current_section = 1

        for i, para in enumerate(doc.paragraphs):
            # Check if paragraph contains an image
            if self._paragraph_has_image(para):
                figure_counter += 1

                # Determine figure number
                if numbering_style == 'by_section':
                    figure_num = f"{current_section}.{figure_counter}"
                else:
                    figure_num = str(figure_counter)

                # Find or create caption
                caption = self._find_figure_caption(doc, i)

                if caption:
                    # Update existing caption
                    self._format_figure_caption(caption, figure_num)
                else:
                    # Create new caption after the figure
                    caption = self._create_figure_caption(doc, i, figure_num)

                figures_info.append({
                    'number': figure_num,
                    'caption': caption.text if caption else None,
                    'paragraph_index': i
                })

            # Track section changes
            elif para.style.name == 'Heading 1':
                if numbering_style == 'by_section':
                    current_section += 1
                    figure_counter = 0

        return {
            'total_figures': len(figures_info),
            'numbering_style': numbering_style,
            'figures': figures_info
        }

    def _paragraph_has_image(self, para) -> bool:
        """Check if paragraph contains an image."""
        for run in para.runs:
            if 'graphic' in run._element.xml or run._element.xpath('.//pic:pic'):
                return True
        return False

    def _find_table_caption(self, doc: Document, table_index: int, table_element) -> Any:
        """Find caption for table (usually paragraph before table)."""
        # Check paragraph immediately before table
        para_index = self._get_paragraph_index_before_element(doc, table_index)

        if para_index is not None and para_index >= 0:
            para = doc.paragraphs[para_index]
            text_lower = para.text.lower()

            if 'таблица' in text_lower:
                return para

        return None

    def _find_figure_caption(self, doc: Document, figure_para_index: int) -> Any:
        """Find caption for figure (usually paragraph after figure)."""
        # Check next paragraph
        if figure_para_index + 1 < len(doc.paragraphs):
            para = doc.paragraphs[figure_para_index + 1]
            text_lower = para.text.lower()

            if 'рисунок' in text_lower or 'рис' in text_lower:
                return para

        return None

    def _format_table_caption(self, para, table_num: str):
        """Format table caption according to GOST."""
        # Extract existing caption text (after number)
        text = para.text
        match = re.search(r'Таблица\s*[\d.]+\s*[-–—]\s*(.+)', text, re.IGNORECASE)
        caption_text = match.group(1) if match else ''

        # Clear and reformat
        para.clear()

        # Add formatted caption
        new_text = f"Таблица {table_num}"
        if caption_text:
            new_text += f" — {caption_text}"

        run = para.add_run(new_text)
        run.font.name = self.FONT_NAME
        run.font.size = Pt(self.FONT_SIZE)

        # Caption above table, aligned right or center
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        para.paragraph_format.space_after = Pt(6)

    def _format_figure_caption(self, para, figure_num: str):
        """Format figure caption according to GOST."""
        # Extract existing caption text
        text = para.text
        match = re.search(r'Рисунок\s*[\d.]+\s*[-–—]\s*(.+)', text, re.IGNORECASE)
        caption_text = match.group(1) if match else ''

        # Clear and reformat
        para.clear()

        # Add formatted caption
        new_text = f"Рисунок {figure_num}"
        if caption_text:
            new_text += f" — {caption_text}"

        run = para.add_run(new_text)
        run.font.name = self.FONT_NAME
        run.font.size = Pt(self.FONT_SIZE)

        # Caption below figure, centered
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_before = Pt(6)
        para.paragraph_format.space_after = Pt(12)

    def _create_table_caption(self, doc: Document, table_element, table_num: str):
        """Create new table caption."""
        # Insert paragraph before table
        # This is complex with python-docx, simplified implementation
        # In production, would need proper XML manipulation
        return None

    def _create_figure_caption(self, doc: Document, figure_index: int, figure_num: str):
        """Create new figure caption."""
        # Insert paragraph after figure
        if figure_index + 1 < len(doc.paragraphs):
            new_para = doc.paragraphs[figure_index].insert_paragraph_before()
            self._format_figure_caption(new_para, figure_num)
            return new_para
        return None

    def _get_paragraph_index(self, doc: Document, element) -> int:
        """Get paragraph index from element."""
        for i, para in enumerate(doc.paragraphs):
            if para._element == element:
                return i
        return -1

    def _get_paragraph_index_before_element(self, doc: Document, element_index: int) -> int:
        """Get index of paragraph before given element index."""
        # Simplified - would need proper implementation
        return element_index - 1 if element_index > 0 else None

    def validate_numbering(self, doc: Document) -> Dict[str, Any]:
        """
        Validate table and figure numbering.

        Args:
            doc: Document to validate

        Returns:
            Validation results
        """
        issues = []

        # Check table numbering
        table_numbers = []
        for para in doc.paragraphs:
            text_lower = para.text.lower()
            if 'таблица' in text_lower:
                match = re.search(r'таблица\s*([\d.]+)', text_lower)
                if match:
                    table_numbers.append(match.group(1))

        # Validate table sequence
        for i, num_str in enumerate(table_numbers):
            expected = i + 1
            try:
                actual = int(num_str.split('.')[0])
                if actual != expected and '.' not in num_str:
                    issues.append(
                        f'Нарушена нумерация таблиц: ожидается {expected}, найдено {num_str}'
                    )
            except ValueError:
                issues.append(f'Некорректный номер таблицы: {num_str}')

        # Check figure numbering
        figure_numbers = []
        for para in doc.paragraphs:
            text_lower = para.text.lower()
            if 'рисунок' in text_lower or 'рис.' in text_lower:
                match = re.search(r'рис(?:унок)?\.?\s*([\d.]+)', text_lower)
                if match:
                    figure_numbers.append(match.group(1))

        # Validate figure sequence
        for i, num_str in enumerate(figure_numbers):
            expected = i + 1
            try:
                actual = int(num_str.split('.')[0])
                if actual != expected and '.' not in num_str:
                    issues.append(
                        f'Нарушена нумерация рисунков: ожидается {expected}, найдено {num_str}'
                    )
            except ValueError:
                issues.append(f'Некорректный номер рисунка: {num_str}')

        return {
            'valid': len(issues) == 0,
            'total_tables': len(table_numbers),
            'total_figures': len(figure_numbers),
            'issues': issues
        }

    def generate_list_of_tables(self, doc: Document) -> str:
        """Generate list of tables for document."""
        tables = []

        for para in doc.paragraphs:
            if 'таблица' in para.text.lower():
                match = re.search(r'Таблица\s*([\d.]+)\s*[-–—]\s*(.+)', para.text, re.IGNORECASE)
                if match:
                    tables.append(f"{match.group(1)}. {match.group(2)}")

        return '\n'.join(tables)

    def generate_list_of_figures(self, doc: Document) -> str:
        """Generate list of figures for document."""
        figures = []

        for para in doc.paragraphs:
            text_lower = para.text.lower()
            if 'рисунок' in text_lower:
                match = re.search(r'Рисунок\s*([\d.]+)\s*[-–—]\s*(.+)', para.text, re.IGNORECASE)
                if match:
                    figures.append(f"{match.group(1)}. {match.group(2)}")

        return '\n'.join(figures)
