# Tests

Тестовый пакет для GOST документного форматера.

## Структура

```
tests/
├── __init__.py
├── conftest.py              # Общие fixtures и конфигурация
├── unit/                    # Unit тесты
│   ├── test_templates.py    # Тесты системы шаблонов
│   └── test_ai_providers.py # Тесты AI провайдеров
└── integration/             # Integration тесты
    └── test_api_documents.py # Тесты API endpoints
```

## Запуск тестов

### Все тесты

```bash
cd backend
pytest
```

### Только unit тесты

```bash
pytest -m unit
```

### Только integration тесты

```bash
pytest -m integration
```

### С покрытием кода

```bash
pytest --cov=app --cov-report=html
```

Отчет будет доступен в `htmlcov/index.html`

### Конкретный файл

```bash
pytest tests/unit/test_templates.py
```

### Конкретный тест

```bash
pytest tests/unit/test_templates.py::TestTemplateFactory::test_create_template_vkr
```

### С детальным выводом

```bash
pytest -v
```

### С выводом print statements

```bash
pytest -s
```

## Написание тестов

### Unit тесты

Unit тесты проверяют отдельные компоненты в изоляции:

```python
import pytest
from app.templates.factory import TemplateFactory

def test_create_template():
    template = TemplateFactory.create_template('gost_vkr')
    assert template.template_name == 'gost_vkr'
```

Используйте декоратор `@pytest.mark.unit` для маркировки unit тестов.

### Integration тесты

Integration тесты проверяют взаимодействие компонентов:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_endpoint(client: AsyncClient):
    response = await client.post('/api/v1/documents/upload', ...)
    assert response.status_code == 200
```

Используйте декоратор `@pytest.mark.integration` для маркировки integration тестов.

### Async тесты

Для асинхронных тестов используйте `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

## Fixtures

Общие fixtures доступны в `conftest.py`:

- `client` - AsyncClient для тестирования API
- `test_db` - Тестовая база данных
- `temp_dir` - Временная директория для тестовых файлов
- `sample_docx_path` - Путь к тестовому DOCX файлу
- `mock_ai_provider` - Mock AI provider

### Использование fixtures

```python
def test_with_fixture(temp_dir):
    file_path = temp_dir / 'test.txt'
    # используйте temp_dir
```

## Mocking

Для мокирования используйте `pytest-mock`:

```python
def test_with_mock(mocker):
    mock_func = mocker.patch('app.services.some_function')
    mock_func.return_value = 'mocked result'

    result = call_function_that_uses_some_function()
    assert result == 'mocked result'
```

## Параметризация

Для тестирования с разными входными данными:

```python
@pytest.mark.parametrize('template_name,expected', [
    ('gost_vkr', GOSTVKRTemplate),
    ('gost_coursework', GOSTCourseworkTemplate),
])
def test_templates(template_name, expected):
    template = TemplateFactory.create_template(template_name)
    assert isinstance(template, expected)
```

## Покрытие кода

Целевое покрытие: **80%+**

Проверить текущее покрытие:

```bash
pytest --cov=app --cov-report=term-missing
```

## CI/CD

Тесты автоматически запускаются при:
- Push в любую ветку
- Создании Pull Request
- Merge в main ветку

Все тесты должны пройти перед слиянием PR.
