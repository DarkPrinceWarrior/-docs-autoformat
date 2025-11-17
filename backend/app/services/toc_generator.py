"""Table of Contents generator for GOST documents."""
from typing import List, Dict, Any
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class TOCEntry:
    """Represents a single TOC entry."""

    def __init__(self, title: str, level: int, page_number: int = None):
        """
        Initialize TOC entry.

        Args:
            title: Heading text
            level: Heading level (1, 2, 3, etc.)
            page_number: Page number where heading appears
        """
        self.title = title
        self.level = level
        self.page_number = page_number

    def __repr__(self):
        return f"TOCEntry(title='{self.title}', level={self.level}, page={self.page_number})"


class TOCGenerator:
    """Generates Table of Contents for GOST documents."""

    FONT_NAME = "Times New Roman"
    FONT_SIZE = 14

    def __init__(self, template_name: str = 'gost_vkr'):
        """
        Initialize TOC generator.

        Args:
            template_name: Name of the GOST template
        """
        self.template_name = template_name

    def generate_toc(self, doc: Document) -> List[TOCEntry]:
        """
        Generate TOC entries from document headings.

        Args:
            doc: Document to generate TOC from

        Returns:
            List of TOC entries
        """
        entries = []

        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                # Extract heading level
                level = self._get_heading_level(para.style.name)
                if level:
                    entry = TOCEntry(
                        title=para.text.strip(),
                        level=level,
                        page_number=None  # Page numbers are complex in python-docx
                    )
                    entries.append(entry)

        return entries

    def insert_toc(
        self,
        doc: Document,
        position: int = 0,
        title: str = "СОДЕРЖАНИЕ"
    ) -> Document:
        """
        Insert TOC into document.

        Args:
            doc: Document to insert TOC into
            position: Paragraph index to insert TOC at (0 = beginning)
            title: TOC title

        Returns:
            Modified document
        """
        entries = self.generate_toc(doc)

        if not entries:
            return doc

        # Calculate insertion position
        insert_index = min(position, len(doc.paragraphs))

        # Insert TOC title
        toc_title = doc.paragraphs[insert_index].insert_paragraph_before(title)
        toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        toc_title.runs[0].font.name = self.FONT_NAME
        toc_title.runs[0].font.size = Pt(self.FONT_SIZE)
        toc_title.runs[0].font.bold = True
        if self.template_name == 'gost_vkr':
            toc_title.runs[0].font.all_caps = True

        # Add spacing after title
        toc_title.paragraph_format.space_after = Pt(12)

        # Insert TOC entries
        for entry in entries:
            self._insert_toc_entry(
                doc,
                entry,
                insert_index + 1 + entries.index(entry)
            )

        # Add page break after TOC
        if insert_index + len(entries) + 1 < len(doc.paragraphs):
            last_toc_para = doc.paragraphs[insert_index + len(entries) + 1]
            self._add_page_break(last_toc_para)

        return doc

    def _insert_toc_entry(self, doc: Document, entry: TOCEntry, position: int):
        """Insert a single TOC entry."""
        # Create paragraph for TOC entry
        para = doc.paragraphs[position].insert_paragraph_before()

        # Set indentation based on level
        indent_cm = (entry.level - 1) * 0.75
        para.paragraph_format.left_indent = Cm(indent_cm)

        # Add text
        run = para.add_run(entry.title)
        run.font.name = self.FONT_NAME
        run.font.size = Pt(self.FONT_SIZE)

        # Add leader dots and page number if available
        if entry.page_number:
            # Add tab with leader
            para.paragraph_format.tab_stops.add_tab_stop(
                Cm(16),  # Position of page number
                alignment=WD_ALIGN_PARAGRAPH.RIGHT
            )

            # Add dots leader (simplified, as proper leader requires complex XML)
            dots = '.' * (100 - len(entry.title) - len(str(entry.page_number)))
            dots_run = para.add_run(' ' + dots + ' ')
            dots_run.font.name = self.FONT_NAME
            dots_run.font.size = Pt(self.FONT_SIZE)

            # Add page number
            page_run = para.add_run(str(entry.page_number))
            page_run.font.name = self.FONT_NAME
            page_run.font.size = Pt(self.FONT_SIZE)

    def _get_heading_level(self, style_name: str) -> int:
        """Extract heading level from style name."""
        if 'Heading 1' in style_name:
            return 1
        elif 'Heading 2' in style_name:
            return 2
        elif 'Heading 3' in style_name:
            return 3
        elif 'Heading' in style_name:
            # Try to extract number
            try:
                return int(style_name.split()[-1])
            except (ValueError, IndexError):
                return 1
        return 0

    def _add_page_break(self, paragraph):
        """Add page break after paragraph."""
        run = paragraph.add_run()
        run.add_break(type=6)  # Page break type

    def update_toc(self, doc: Document, toc_title: str = "СОДЕРЖАНИЕ") -> Document:
        """
        Update existing TOC or insert new one.

        Args:
            doc: Document to update
            toc_title: Title of TOC section

        Returns:
            Modified document
        """
        # Find existing TOC
        toc_index = None
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip().upper() == toc_title.upper():
                toc_index = i
                break

        if toc_index is not None:
            # Remove old TOC entries
            # This is simplified - in production, you'd want more sophisticated detection
            entries_to_remove = []
            for i in range(toc_index + 1, min(toc_index + 50, len(doc.paragraphs))):
                # Stop at first heading or significant content
                if doc.paragraphs[i].style.name.startswith('Heading'):
                    break
                entries_to_remove.append(i)

            # Remove in reverse order to maintain indices
            for i in reversed(entries_to_remove):
                p = doc.paragraphs[i]
                p._element.getparent().remove(p._element)

            # Insert new TOC
            return self.insert_toc(doc, toc_index + 1, title="")
        else:
            # Insert new TOC at beginning
            return self.insert_toc(doc, 0, title=toc_title)

    def get_toc_structure(self, doc: Document) -> Dict[str, Any]:
        """
        Get TOC structure as a dictionary.

        Args:
            doc: Document to analyze

        Returns:
            Dictionary with TOC structure
        """
        entries = self.generate_toc(doc)

        structure = {
            'title': 'СОДЕРЖАНИЕ',
            'total_entries': len(entries),
            'entries': []
        }

        for entry in entries:
            structure['entries'].append({
                'title': entry.title,
                'level': entry.level,
                'page': entry.page_number
            })

        # Build hierarchy
        hierarchy = self._build_hierarchy(entries)
        structure['hierarchy'] = hierarchy

        return structure

    def _build_hierarchy(self, entries: List[TOCEntry]) -> List[Dict[str, Any]]:
        """Build hierarchical structure from flat list of entries."""
        hierarchy = []
        stack = []

        for entry in entries:
            node = {
                'title': entry.title,
                'level': entry.level,
                'children': []
            }

            # Pop stack until we find parent level
            while stack and stack[-1]['level'] >= entry.level:
                stack.pop()

            # Add to parent or root
            if stack:
                stack[-1]['children'].append(node)
            else:
                hierarchy.append(node)

            stack.append(node)

        return hierarchy
