# Система шаблонов форматирования

Приложение поддерживает модульную систему шаблонов, позволяющую форматировать документы согласно различным стандартам и требованиям.

## Доступные шаблоны

### 1. GOST VKR (gost_vkr) - По умолчанию

**Назначение**: Выпускные квалификационные работы по ГОСТ 7.32-2017

**Особенности**:
- Заголовки первого уровня: ПРОПИСНЫМИ БУКВАМИ, по центру, жирный
- Заголовки второго уровня: Обычный регистр, жирный, с отступом
- Заголовки третьего уровня: Обычный регистр, жирный, с отступом
- Шрифт: Times New Roman, 14pt
- Интервал: 1.5
- Поля: левое 3см, правое 1см, верхнее и нижнее 2см
- Отступ абзаца: 1.25см
- Выравнивание: по ширине
- Список литературы: по ГОСТ 7.0.5-2008

**Когда использовать**:
- Дипломные работы
- Магистерские диссертации
- Выпускные квалификационные работы
- Научные отчеты

### 2. GOST Coursework (gost_coursework)

**Назначение**: Курсовые работы и проекты

**Особенности**:
- Заголовки первого уровня: Обычный регистр (не прописные), по центру, жирный
- Заголовки второго и третьего уровня: жирный, с отступом
- Шрифт: Times New Roman, 14pt
- Интервал: 1.5
- Поля: левое 3см, правое 1.5см, верхнее и нижнее 2см
- Отступ абзаца: 1.25см
- Выравнивание: по ширине
- Упрощенное форматирование списка литературы

**Когда использовать**:
- Курсовые работы
- Курсовые проекты
- Рефераты
- Семестровые работы

**Отличия от GOST VKR**:
- Заголовки в обычном регистре (не все прописные)
- Немного шире правое поле (1.5см вместо 1см)
- Более гибкое определение структуры для коротких работ
- Поддержка различных форматов нумерации в списке литературы

## Использование шаблонов

### Через API

**Загрузка документа с выбором шаблона**:

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@document.docx" \
  -F "template=gost_coursework"
```

**Получение списка доступных шаблонов**:

```bash
curl "http://localhost:8000/api/v1/documents/templates"
```

Ответ:
```json
[
  {
    "name": "gost_vkr",
    "description": "Выпускная квалификационная работа (ВКР) по ГОСТ 7.32-2017",
    "font": "Times New Roman",
    "font_size": "14",
    "line_spacing": "1.5"
  },
  {
    "name": "gost_coursework",
    "description": "Курсовая работа по ГОСТ (упрощенный вариант)",
    "font": "Times New Roman",
    "font_size": "14",
    "line_spacing": "1.5"
  }
]
```

### Из кода Python

```python
from app.services.docx_processor import DocxProcessor

# Использование шаблона для ВКР
processor_vkr = DocxProcessor(template_name="gost_vkr")
await processor_vkr.process_document("input.docx", "output_vkr.docx")

# Использование шаблона для курсовой
processor_course = DocxProcessor(template_name="gost_coursework")
await processor_course.process_document("input.docx", "output_course.docx")
```

## Создание собственного шаблона

### Шаг 1: Создайте класс шаблона

Создайте новый файл `backend/app/templates/my_template.py`:

```python
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any
from app.templates.base import BaseTemplate


class MyCustomTemplate(BaseTemplate):
    """Мой пользовательский шаблон"""

    # Переопределите константы при необходимости
    FONT_SIZE = 12
    MARGIN_LEFT = 2.5

    @property
    def template_name(self) -> str:
        return "my_template"

    @property
    def template_description(self) -> str:
        return "Мой пользовательский шаблон форматирования"

    def apply_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
        """Применяет форматирование к документу"""

        # Применяем настройки страницы
        self._apply_page_settings(doc)

        # Создаем стили
        self._create_document_styles(doc)

        # Применяем форматирование к параграфам
        self._format_paragraphs(doc, structure)

        return doc

    def _create_document_styles(self, doc: Document):
        """Создает стили документа"""

        # Создаем базовые стили
        self._create_base_styles(doc)

        # Создаем стили заголовков
        self._create_heading_style(
            doc,
            'Heading 1',
            font_size=16,
            bold=True,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )

    def _format_paragraphs(self, doc: Document, structure: Dict[str, Any]):
        """Форматирует параграфы"""
        # Ваша логика форматирования
        pass
```

### Шаг 2: Зарегистрируйте шаблон

В файле `backend/app/templates/factory.py`:

```python
from app.templates.my_template import MyCustomTemplate

class TemplateFactory:
    _templates = {
        "gost_vkr": GOSTVKRTemplate,
        "gost_coursework": GOSTCourseworkTemplate,
        "my_template": MyCustomTemplate,  # Добавьте свой шаблон
    }
```

### Шаг 3: Используйте шаблон

```python
processor = DocxProcessor(template_name="my_template")
await processor.process_document("input.docx", "output.docx")
```

## Базовый класс BaseTemplate

Все шаблоны наследуются от `BaseTemplate` и получают доступ к следующим методам:

### Константы (могут быть переопределены)

```python
FONT_NAME = "Times New Roman"
FONT_SIZE = 14
LINE_SPACING = 1.5
PARAGRAPH_INDENT = 1.25  # см
MARGIN_TOP = 2.0
MARGIN_BOTTOM = 2.0
MARGIN_LEFT = 3.0
MARGIN_RIGHT = 1.0
```

### Полезные методы

- `_apply_page_settings(doc)` - применяет настройки полей
- `_create_base_styles(doc)` - создает базовый стиль Normal
- `_create_heading_style(doc, name, **params)` - создает стиль заголовка
- `_apply_paragraph_style(paragraph, style_name)` - применяет стиль к параграфу
- `_remove_trailing_period(paragraph)` - удаляет точку в конце заголовка

### Обязательные методы для реализации

```python
@property
def template_name(self) -> str:
    """Уникальное имя шаблона"""
    pass

@property
def template_description(self) -> str:
    """Описание шаблона"""
    pass

def apply_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
    """Основной метод форматирования"""
    pass
```

## Сравнение шаблонов

| Параметр | GOST VKR | GOST Coursework |
|----------|----------|-----------------|
| **Назначение** | ВКР, дипломы | Курсовые работы |
| **Заголовок 1** | ПРОПИСНЫЕ, центр | Обычный, центр |
| **Правое поле** | 1 см | 1.5 см |
| **Строгость** | Высокая | Средняя |
| **Список литературы** | ГОСТ 7.0.5-2008 | Упрощенный |

## Лучшие практики

1. **Наследуйтесь от BaseTemplate** - используйте готовые методы
2. **Переопределяйте только нужное** - не дублируйте код
3. **Используйте константы** - для легкой настройки
4. **Документируйте отличия** - объясните, чем ваш шаблон особенный
5. **Тестируйте на реальных документах** - проверьте все случаи

## Примеры использования AI анализа в шаблонах

Структура документа из AI анализа доступна в методе `apply_formatting`:

```python
def apply_formatting(self, doc: Document, structure: Dict[str, Any]) -> Document:
    elements = structure.get('elements', [])

    for element in elements:
        element_type = element.get('type')  # chapter, introduction, etc.
        level = element.get('level')  # 1, 2, 3
        title = element.get('title')  # Текст заголовка
        number = element.get('number')  # Номер элемента

        # Используйте информацию для точного форматирования
```

## Добавление миграции БД

При добавлении нового шаблона как значения по умолчанию, обновите миграцию базы данных:

```bash
cd backend
alembic revision --autogenerate -m "Add new template"
alembic upgrade head
```

## FAQ

**Q: Можно ли изменить шаблон для уже загруженного документа?**
A: Нет, шаблон применяется при загрузке. Загрузите документ заново с другим шаблоном.

**Q: Как добавить поддержку других стандартов (APA, MLA)?**
A: Создайте новый класс шаблона, наследующий BaseTemplate, и зарегистрируйте его в фабрике.

**Q: Можно ли комбинировать шаблоны?**
A: Можно создать шаблон, который использует элементы других шаблонов через наследование или композицию.

## Поддержка и вклад

При создании нового шаблона, рассмотрите возможность поделиться им с сообществом:

1. Создайте issue с описанием шаблона
2. Предоставьте примеры документов
3. Укажите стандарт или требования, которым соответствует шаблон
