"""Bibliography formatter for GOST 7.0.5-2008."""
from typing import List, Dict, Any
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re


class BibliographyEntry:
    """Represents a bibliography entry."""

    def __init__(
        self,
        authors: str = None,
        title: str = None,
        publisher: str = None,
        year: str = None,
        pages: str = None,
        url: str = None,
        entry_type: str = 'book'
    ):
        """
        Initialize bibliography entry.

        Args:
            authors: Authors (Last Name, Initials)
            title: Title of work
            publisher: Publisher information
            year: Year of publication
            pages: Page count or range
            url: URL for online resources
            entry_type: Type of entry (book, article, website, etc.)
        """
        self.authors = authors
        self.title = title
        self.publisher = publisher
        self.year = year
        self.pages = pages
        self.url = url
        self.entry_type = entry_type

    def format_gost(self, number: int = None) -> str:
        """
        Format entry according to GOST 7.0.5-2008.

        Args:
            number: Entry number in bibliography

        Returns:
            Formatted string
        """
        parts = []

        # Add number
        if number:
            parts.append(f"{number}.")

        # Add authors
        if self.authors:
            parts.append(self.authors)

        # Add title
        if self.title:
            if parts and not parts[-1].endswith('.'):
                parts[-1] += '.'
            parts.append(self.title)

        # Add publisher info
        if self.publisher:
            if parts and not parts[-1].endswith('.'):
                parts[-1] += '.'
            publisher_parts = []
            if self.publisher:
                publisher_parts.append(self.publisher)
            if self.year:
                publisher_parts.append(str(self.year))
            if publisher_parts:
                parts.append(', '.join(publisher_parts))

        # Add pages
        if self.pages:
            if parts and not parts[-1].endswith('.'):
                parts[-1] += '.'
            parts.append(f"{self.pages} с.")

        # Add URL for online resources
        if self.url:
            if parts and not parts[-1].endswith('.'):
                parts[-1] += '.'
            parts.append(f"URL: {self.url}")

        result = ' '.join(parts)
        if not result.endswith('.'):
            result += '.'

        return result


class BibliographyFormatter:
    """Formats bibliography section according to GOST."""

    FONT_NAME = "Times New Roman"
    FONT_SIZE = 14
    LINE_SPACING = 1.0  # Single spacing for bibliography

    def __init__(self, template_name: str = 'gost_vkr'):
        """
        Initialize bibliography formatter.

        Args:
            template_name: Name of the GOST template
        """
        self.template_name = template_name

    def find_bibliography_section(self, doc: Document) -> int:
        """
        Find bibliography section in document.

        Args:
            doc: Document to search

        Returns:
            Index of bibliography heading, or None
        """
        keywords = [
            'список литературы',
            'библиографический список',
            'список использованных источников',
            'список источников'
        ]

        for i, para in enumerate(doc.paragraphs):
            text_lower = para.text.strip().lower()
            if any(keyword in text_lower for keyword in keywords):
                return i

        return None

    def extract_bibliography_entries(
        self,
        doc: Document,
        start_index: int
    ) -> List[str]:
        """
        Extract bibliography entries from document.

        Args:
            doc: Document to extract from
            start_index: Index to start extraction from

        Returns:
            List of raw entry strings
        """
        entries = []
        current_entry = []

        # Start from next paragraph after heading
        for i in range(start_index + 1, len(doc.paragraphs)):
            para = doc.paragraphs[i]

            # Stop at next heading
            if para.style.name.startswith('Heading'):
                break

            text = para.text.strip()
            if not text:
                if current_entry:
                    entries.append(' '.join(current_entry))
                    current_entry = []
                continue

            # Check if this starts a new entry (numbered)
            if re.match(r'^\d+\.', text):
                if current_entry:
                    entries.append(' '.join(current_entry))
                current_entry = [text]
            else:
                current_entry.append(text)

        # Add last entry
        if current_entry:
            entries.append(' '.join(current_entry))

        return entries

    def parse_entry(self, entry_text: str) -> BibliographyEntry:
        """
        Parse entry text into structured BibliographyEntry.

        This is a simplified parser - real implementation would need
        more sophisticated parsing logic.

        Args:
            entry_text: Raw entry text

        Returns:
            BibliographyEntry object
        """
        # Remove number prefix
        text = re.sub(r'^\d+\.\s*', '', entry_text)

        # Try to extract URL
        url_match = re.search(r'URL:\s*(\S+)', text)
        url = url_match.group(1) if url_match else None
        if url:
            text = text.replace(url_match.group(0), '').strip()

        # Try to extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        year = year_match.group(0) if year_match else None

        # Try to extract pages
        pages_match = re.search(r'(\d+)\s*с\.', text)
        pages = pages_match.group(1) if pages_match else None

        # Split by common delimiters
        parts = text.split('//')
        if len(parts) >= 2:
            authors_title = parts[0].strip()
            publisher_info = parts[1].strip()
        else:
            parts = text.split('.')
            authors_title = parts[0].strip() if parts else text
            publisher_info = '.'.join(parts[1:]).strip() if len(parts) > 1 else None

        return BibliographyEntry(
            authors=None,  # Would need more sophisticated parsing
            title=authors_title,
            publisher=publisher_info,
            year=year,
            pages=pages,
            url=url
        )

    def format_bibliography_section(
        self,
        doc: Document,
        entries: List[BibliographyEntry],
        start_index: int = None
    ) -> Document:
        """
        Format bibliography section in document.

        Args:
            doc: Document to format
            entries: List of bibliography entries
            start_index: Index to insert bibliography at

        Returns:
            Modified document
        """
        if start_index is None:
            # Add at end
            start_index = len(doc.paragraphs)

            # Add heading
            heading = doc.add_paragraph('СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ')
            heading.style = doc.styles['Heading 1']
        else:
            # Use existing heading
            heading = doc.paragraphs[start_index]

        # Format heading
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if heading.runs:
            heading.runs[0].font.name = self.FONT_NAME
            heading.runs[0].font.size = Pt(self.FONT_SIZE)
            heading.runs[0].font.bold = True
            if self.template_name == 'gost_vkr':
                heading.runs[0].font.all_caps = True

        # Add entries
        for i, entry in enumerate(entries, 1):
            para = doc.add_paragraph()

            # Format as numbered list with hanging indent
            para.paragraph_format.left_indent = Cm(1.25)
            para.paragraph_format.first_line_indent = Cm(-1.25)
            para.paragraph_format.line_spacing = self.LINE_SPACING
            para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

            # Add text
            run = para.add_run(entry.format_gost(i))
            run.font.name = self.FONT_NAME
            run.font.size = Pt(self.FONT_SIZE)

        return doc

    def validate_bibliography(
        self,
        doc: Document
    ) -> Dict[str, Any]:
        """
        Validate bibliography section.

        Args:
            doc: Document to validate

        Returns:
            Validation results
        """
        issues = []
        bib_index = self.find_bibliography_section(doc)

        if bib_index is None:
            return {
                'valid': False,
                'issues': ['Раздел библиографии не найден'],
                'entries_count': 0
            }

        entries = self.extract_bibliography_entries(doc, bib_index)

        # Check numbering
        expected_num = 1
        for entry in entries:
            match = re.match(r'^(\d+)\.', entry)
            if match:
                num = int(match.group(1))
                if num != expected_num:
                    issues.append(
                        f'Неправильная нумерация: ожидается {expected_num}, найдено {num}'
                    )
                expected_num += 1
            else:
                issues.append(f'Запись не начинается с номера: {entry[:50]}...')

        # Check formatting
        for entry in entries:
            if not entry.endswith('.'):
                issues.append(f'Запись должна заканчиваться точкой: {entry[:50]}...')

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'entries_count': len(entries),
            'entries': entries[:5]  # First 5 entries for preview
        }

    def sort_bibliography(
        self,
        entries: List[BibliographyEntry],
        sort_by: str = 'author'
    ) -> List[BibliographyEntry]:
        """
        Sort bibliography entries.

        Args:
            entries: List of entries to sort
            sort_by: Sort criteria ('author', 'title', 'year')

        Returns:
            Sorted list
        """
        if sort_by == 'author':
            return sorted(entries, key=lambda e: e.authors or e.title or '')
        elif sort_by == 'title':
            return sorted(entries, key=lambda e: e.title or '')
        elif sort_by == 'year':
            return sorted(entries, key=lambda e: e.year or '0', reverse=True)
        else:
            return entries
