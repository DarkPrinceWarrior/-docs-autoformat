"""GOST document validator."""
from typing import Dict, List, Any
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH


class ValidationIssue:
    """Represents a validation issue found in the document."""

    def __init__(
        self,
        severity: str,
        category: str,
        message: str,
        location: str = None,
        suggestion: str = None
    ):
        """
        Initialize validation issue.

        Args:
            severity: 'error', 'warning', or 'info'
            category: Category of the issue (e.g., 'formatting', 'structure')
            message: Description of the issue
            location: Where the issue was found
            suggestion: How to fix the issue
        """
        self.severity = severity
        self.category = category
        self.message = message
        self.location = location
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'severity': self.severity,
            'category': self.category,
            'message': self.message,
            'location': self.location,
            'suggestion': self.suggestion
        }


class GOSTValidator:
    """Validator for GOST 7.32-2017 compliance."""

    # Expected values
    EXPECTED_FONT = "Times New Roman"
    EXPECTED_FONT_SIZE = 14
    EXPECTED_LINE_SPACING = 1.5
    EXPECTED_INDENT = 1.25
    EXPECTED_MARGIN_LEFT = 3.0
    EXPECTED_MARGIN_RIGHT = 1.0
    EXPECTED_MARGIN_TOP = 2.0
    EXPECTED_MARGIN_BOTTOM = 2.0

    # Tolerances
    MARGIN_TOLERANCE = 0.2  # cm
    SIZE_TOLERANCE = 1  # pt

    def __init__(self, template_name: str = 'gost_vkr'):
        """
        Initialize validator.

        Args:
            template_name: Name of the GOST template to validate against
        """
        self.template_name = template_name
        self.issues: List[ValidationIssue] = []

        # Adjust expectations for coursework template
        if template_name == 'gost_coursework':
            self.EXPECTED_MARGIN_RIGHT = 1.5

    def validate_document(self, doc_path: str) -> Dict[str, Any]:
        """
        Validate document against GOST requirements.

        Args:
            doc_path: Path to the document to validate

        Returns:
            Dictionary with validation results
        """
        self.issues = []
        doc = Document(doc_path)

        self._validate_page_settings(doc)
        self._validate_paragraphs(doc)
        self._validate_headings(doc)
        self._validate_structure(doc)

        return self._generate_report()

    def _validate_page_settings(self, doc: Document):
        """Validate page settings (margins, orientation)."""
        if not doc.sections:
            self.issues.append(ValidationIssue(
                severity='error',
                category='page_settings',
                message='Документ не содержит разделов',
                suggestion='Документ должен иметь хотя бы один раздел'
            ))
            return

        section = doc.sections[0]

        # Check margins
        margin_issues = []

        left_margin = section.left_margin.cm
        if abs(left_margin - self.EXPECTED_MARGIN_LEFT) > self.MARGIN_TOLERANCE:
            margin_issues.append(
                f'Левое поле: {left_margin:.1f} см (ожидается {self.EXPECTED_MARGIN_LEFT} см)'
            )

        right_margin = section.right_margin.cm
        if abs(right_margin - self.EXPECTED_MARGIN_RIGHT) > self.MARGIN_TOLERANCE:
            margin_issues.append(
                f'Правое поле: {right_margin:.1f} см (ожидается {self.EXPECTED_MARGIN_RIGHT} см)'
            )

        top_margin = section.top_margin.cm
        if abs(top_margin - self.EXPECTED_MARGIN_TOP) > self.MARGIN_TOLERANCE:
            margin_issues.append(
                f'Верхнее поле: {top_margin:.1f} см (ожидается {self.EXPECTED_MARGIN_TOP} см)'
            )

        bottom_margin = section.bottom_margin.cm
        if abs(bottom_margin - self.EXPECTED_MARGIN_BOTTOM) > self.MARGIN_TOLERANCE:
            margin_issues.append(
                f'Нижнее поле: {bottom_margin:.1f} см (ожидается {self.EXPECTED_MARGIN_BOTTOM} см)'
            )

        if margin_issues:
            self.issues.append(ValidationIssue(
                severity='error',
                category='page_settings',
                message='Некорректные поля документа',
                location='Параметры страницы',
                suggestion='; '.join(margin_issues)
            ))

    def _validate_paragraphs(self, doc: Document):
        """Validate paragraph formatting."""
        normal_paragraphs = [
            p for p in doc.paragraphs
            if p.style.name.startswith('Normal') or p.style.name.startswith('Body')
        ]

        for i, para in enumerate(normal_paragraphs[:10]):  # Check first 10 paragraphs
            if not para.text.strip():
                continue

            # Check font
            if para.runs:
                font_name = para.runs[0].font.name
                if font_name and font_name != self.EXPECTED_FONT:
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        category='formatting',
                        message=f'Неправильный шрифт: {font_name}',
                        location=f'Абзац {i + 1}',
                        suggestion=f'Используйте {self.EXPECTED_FONT}'
                    ))

                # Check font size
                font_size = para.runs[0].font.size
                if font_size:
                    size_pt = font_size.pt
                    if abs(size_pt - self.EXPECTED_FONT_SIZE) > self.SIZE_TOLERANCE:
                        self.issues.append(ValidationIssue(
                            severity='warning',
                            category='formatting',
                            message=f'Неправильный размер шрифта: {size_pt} пт',
                            location=f'Абзац {i + 1}',
                            suggestion=f'Используйте {self.EXPECTED_FONT_SIZE} пт'
                        ))

            # Check line spacing
            if para.paragraph_format.line_spacing:
                spacing = para.paragraph_format.line_spacing
                if abs(spacing - self.EXPECTED_LINE_SPACING) > 0.1:
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        category='formatting',
                        message=f'Неправильный межстрочный интервал: {spacing}',
                        location=f'Абзац {i + 1}',
                        suggestion=f'Используйте интервал {self.EXPECTED_LINE_SPACING}'
                    ))

            # Check alignment
            if para.paragraph_format.alignment not in [WD_ALIGN_PARAGRAPH.JUSTIFY, None]:
                self.issues.append(ValidationIssue(
                    severity='info',
                    category='formatting',
                    message='Текст не выровнен по ширине',
                    location=f'Абзац {i + 1}',
                    suggestion='Используйте выравнивание по ширине'
                ))

    def _validate_headings(self, doc: Document):
        """Validate heading formatting."""
        headings = [p for p in doc.paragraphs if p.style.name.startswith('Heading')]

        for heading in headings:
            # Check that headings don't end with a period
            if heading.text.strip().endswith('.'):
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='headings',
                    message='Заголовок не должен заканчиваться точкой',
                    location=f'Заголовок: "{heading.text[:50]}..."',
                    suggestion='Удалите точку в конце заголовка'
                ))

            # Check alignment for VKR template
            if self.template_name == 'gost_vkr':
                if heading.paragraph_format.alignment != WD_ALIGN_PARAGRAPH.CENTER:
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        category='headings',
                        message='Заголовок должен быть выровнен по центру',
                        location=f'Заголовок: "{heading.text[:50]}..."',
                        suggestion='Установите выравнивание по центру'
                    ))

    def _validate_structure(self, doc: Document):
        """Validate document structure."""
        # Check if document has content
        if not doc.paragraphs or all(not p.text.strip() for p in doc.paragraphs):
            self.issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='Документ пуст или не содержит текста',
                suggestion='Добавьте содержимое в документ'
            ))
            return

        # Check if document has headings
        headings = [p for p in doc.paragraphs if p.style.name.startswith('Heading')]
        if not headings:
            self.issues.append(ValidationIssue(
                severity='warning',
                category='structure',
                message='Документ не содержит заголовков',
                suggestion='Добавьте заголовки разделов'
            ))

        # Check for common required sections (for VKR)
        if self.template_name == 'gost_vkr':
            text_lower = ' '.join(p.text.lower() for p in doc.paragraphs)

            required_sections = {
                'введение': 'Раздел "Введение"',
                'заключение': 'Раздел "Заключение"',
                'список': 'Список литературы'
            }

            for keyword, section_name in required_sections.items():
                if keyword not in text_lower:
                    self.issues.append(ValidationIssue(
                        severity='info',
                        category='structure',
                        message=f'Не найден обязательный раздел: {section_name}',
                        suggestion=f'Добавьте {section_name}'
                    ))

    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        errors = [issue for issue in self.issues if issue.severity == 'error']
        warnings = [issue for issue in self.issues if issue.severity == 'warning']
        info = [issue for issue in self.issues if issue.severity == 'info']

        is_valid = len(errors) == 0

        return {
            'valid': is_valid,
            'template': self.template_name,
            'summary': {
                'total_issues': len(self.issues),
                'errors': len(errors),
                'warnings': len(warnings),
                'info': len(info)
            },
            'issues': {
                'errors': [issue.to_dict() for issue in errors],
                'warnings': [issue.to_dict() for issue in warnings],
                'info': [issue.to_dict() for issue in info]
            },
            'compliance_score': self._calculate_compliance_score()
        }

    def _calculate_compliance_score(self) -> float:
        """
        Calculate compliance score (0-100).

        Errors: -10 points each
        Warnings: -3 points each
        Info: -1 point each
        """
        score = 100.0

        for issue in self.issues:
            if issue.severity == 'error':
                score -= 10
            elif issue.severity == 'warning':
                score -= 3
            elif issue.severity == 'info':
                score -= 1

        return max(0.0, min(100.0, score))
