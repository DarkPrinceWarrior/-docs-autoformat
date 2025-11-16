# Использование локальных моделей

Приложение GOST Document Formatter поддерживает три типа AI-провайдеров для анализа структуры документов:

1. **Claude API** (облачный)
2. **Ollama** (локальные модели)
3. **Custom API** (пользовательские OpenAI-совместимые API)

## 1. Claude API (по умолчанию)

Claude API от Anthropic - облачный сервис с высокой точностью анализа.

### Настройка:

```env
AI_PROVIDER=claude
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### Получение API ключа:

1. Зарегистрируйтесь на https://console.anthropic.com
2. Создайте API ключ в разделе API Keys
3. Добавьте ключ в `.env` файл

## 2. Ollama (локальные модели)

Ollama позволяет запускать большие языковые модели локально на вашем компьютере без отправки данных в облако.

### Преимущества:
- Полная конфиденциальность данных
- Отсутствие затрат на API
- Работа без интернета
- Возможность кастомизации моделей

### Установка Ollama:

#### Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### macOS:
```bash
brew install ollama
```

#### Windows:
Скачайте установщик с https://ollama.com/download

### Запуск Ollama:

```bash
ollama serve
```

Ollama будет доступен на `http://localhost:11434`

### Скачивание и запуск моделей:

Рекомендуемые модели для анализа документов:

**Llama 3.1** (рекомендуется):
```bash
ollama pull llama3.1
ollama run llama3.1
```

**Mistral**:
```bash
ollama pull mistral
ollama run mistral
```

**Phi-3** (легковесная):
```bash
ollama pull phi3
ollama run phi3
```

**DeepSeek Coder** (хорош для структурированного вывода):
```bash
ollama pull deepseek-coder
ollama run deepseek-coder
```

### Настройка в приложении:

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### Использование с Docker:

Если Ollama запущен на хост-машине, а приложение в Docker, используйте:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Для Linux Docker:
```env
OLLAMA_BASE_URL=http://172.17.0.1:11434
```

### Доступные модели:

Полный список моделей: https://ollama.com/library

| Модель | Размер | RAM | Качество |
|--------|--------|-----|----------|
| llama3.1 | 4.7GB | 8GB | Отлично |
| mistral | 4.1GB | 8GB | Хорошо |
| phi3 | 2.3GB | 4GB | Среднее |
| deepseek-coder | 3.8GB | 8GB | Хорошо |
| gemma2 | 5.4GB | 8GB | Отлично |

## 3. Custom API (пользовательские API)

Поддержка OpenAI-совместимых API позволяет использовать:
- OpenAI API
- LM Studio
- LocalAI
- Text Generation WebUI
- vLLM
- Другие совместимые сервисы

### Настройка для OpenAI:

```env
AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.openai.com
CUSTOM_API_KEY=sk-your-openai-api-key
CUSTOM_API_MODEL=gpt-3.5-turbo
```

### Настройка для LM Studio:

LM Studio - графический интерфейс для запуска локальных моделей с OpenAI-совместимым API.

1. Скачайте LM Studio: https://lmstudio.ai
2. Загрузите модель (например, Llama 3.1)
3. Запустите локальный сервер (вкладка "Local Server")
4. Настройте приложение:

```env
AI_PROVIDER=custom
CUSTOM_API_BASE_URL=http://localhost:1234
CUSTOM_API_KEY=  # Оставьте пустым для LM Studio
CUSTOM_API_MODEL=llama-3.1-8b-instruct
```

### Настройка для LocalAI:

LocalAI - самохостинговая альтернатива OpenAI.

1. Запустите LocalAI:
```bash
docker run -p 8080:8080 localai/localai:latest
```

2. Настройте приложение:
```env
AI_PROVIDER=custom
CUSTOM_API_BASE_URL=http://localhost:8080
CUSTOM_API_KEY=  # Обычно не требуется
CUSTOM_API_MODEL=llama-3
```

### Настройка для Text Generation WebUI:

```bash
# Запустите с API флагом
python server.py --api
```

```env
AI_PROVIDER=custom
CUSTOM_API_BASE_URL=http://localhost:5000
CUSTOM_API_MODEL=your-model-name
```

## Сравнение провайдеров

| Провайдер | Конфиденциальность | Стоимость | Качество | Скорость |
|-----------|-------------------|-----------|----------|----------|
| Claude API | Низкая (облако) | Платный | Отличное | Высокая |
| Ollama | Высокая (локально) | Бесплатный | Хорошее | Средняя* |
| LM Studio | Высокая (локально) | Бесплатный | Хорошее | Средняя* |
| OpenAI | Низкая (облако) | Платный | Отличное | Высокая |

*Скорость зависит от мощности вашего компьютера и наличия GPU

## Требования к оборудованию для локальных моделей

### Минимальные требования:
- CPU: 4+ ядра
- RAM: 8GB
- Диск: 10GB свободного места

### Рекомендуемые:
- CPU: 8+ ядер или GPU (NVIDIA/AMD)
- RAM: 16GB+
- Диск: 20GB+ SSD

### Оптимальные (с GPU):
- NVIDIA GPU с 8GB+ VRAM
- RAM: 16GB+
- Значительно ускоряет обработку

## Ускорение с GPU

### Ollama с GPU:

Ollama автоматически использует GPU, если доступен:

**NVIDIA:**
```bash
# Убедитесь, что установлены драйвера CUDA
nvidia-smi

# Ollama автоматически определит GPU
ollama run llama3.1
```

**AMD (ROCm):**
```bash
# Установите ROCm
# Ollama поддерживает AMD GPU
```

**Apple Silicon (M1/M2/M3):**
```bash
# Ollama оптимизирован для Apple Silicon
# Использует Metal для ускорения
```

## Устранение неполадок

### Ollama не отвечает:

```bash
# Проверьте, что Ollama запущен
curl http://localhost:11434/api/version

# Перезапустите Ollama
ollama serve
```

### Модель работает медленно:

1. Используйте меньшую модель (phi3 вместо llama3.1)
2. Проверьте использование GPU:
```bash
ollama ps  # Должно показать использование GPU
```
3. Увеличьте доступную RAM

### Ошибка подключения в Docker:

Для Linux используйте network mode host в docker-compose.yml:

```yaml
backend:
  network_mode: host
  environment:
    - OLLAMA_BASE_URL=http://localhost:11434
```

Или добавьте Ollama в Docker Compose:

```yaml
ollama:
  image: ollama/ollama:latest
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

## Переключение между провайдерами

Просто измените `AI_PROVIDER` в `.env` и перезапустите приложение:

```bash
# Используем Ollama
AI_PROVIDER=ollama

# Перезапуск
docker-compose restart backend celery_worker
```

## Рекомендации по выбору

**Используйте Claude API если:**
- Нужна максимальная точность
- Есть бюджет на API
- Работаете с конфиденциальными данными нечасто

**Используйте Ollama если:**
- Важна конфиденциальность
- Нет бюджета на API
- Есть мощный компьютер/сервер
- Обрабатываете много документов

**Используйте Custom API если:**
- Уже используете OpenAI или аналоги
- Хотите гибкость в выборе моделей
- Используете корпоративное решение

## Дополнительные ресурсы

- Ollama: https://ollama.com
- LM Studio: https://lmstudio.ai
- LocalAI: https://localai.io
- Claude API: https://console.anthropic.com
- OpenAI API: https://platform.openai.com
