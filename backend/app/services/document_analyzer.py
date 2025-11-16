from typing import Dict, Any
from app.core.config import settings
from app.services.ai_providers.factory import AIProviderFactory
from app.services.ai_providers.base import BaseAIProvider


class DocumentAnalyzer:
    """Универсальный сервис для анализа структуры документа с использованием AI"""

    def __init__(self, provider: BaseAIProvider = None):
        """
        Инициализация анализатора документов

        Args:
            provider: Экземпляр AI-провайдера. Если не указан, создается автоматически
                     на основе настроек из конфигурации
        """
        if provider is None:
            provider = self._create_provider_from_settings()

        self.provider = provider

    def _create_provider_from_settings(self) -> BaseAIProvider:
        """Создает провайдер на основе настроек конфигурации"""

        provider_type = settings.AI_PROVIDER.lower()

        if provider_type == "claude":
            if not settings.CLAUDE_API_KEY:
                raise ValueError(
                    "CLAUDE_API_KEY не указан в настройках. "
                    "Пожалуйста, установите его в .env файле"
                )

            return AIProviderFactory.create_provider(
                provider_type="claude",
                api_key=settings.CLAUDE_API_KEY,
                model=settings.CLAUDE_MODEL
            )

        elif provider_type == "ollama":
            return AIProviderFactory.create_provider(
                provider_type="ollama",
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL
            )

        elif provider_type == "custom":
            if not settings.CUSTOM_API_BASE_URL:
                raise ValueError(
                    "CUSTOM_API_BASE_URL не указан в настройках. "
                    "Пожалуйста, установите его в .env файле"
                )

            return AIProviderFactory.create_provider(
                provider_type="custom",
                base_url=settings.CUSTOM_API_BASE_URL,
                api_key=settings.CUSTOM_API_KEY,
                model=settings.CUSTOM_API_MODEL
            )

        else:
            raise ValueError(
                f"Неподдерживаемый AI_PROVIDER: {provider_type}. "
                f"Доступные значения: 'claude', 'ollama', 'custom'"
            )

    async def analyze_document_structure(self, text_content: str) -> Dict[str, Any]:
        """
        Анализирует структуру документа и определяет разделы

        Args:
            text_content: Текстовое содержимое документа

        Returns:
            Словарь с результатами анализа структуры
        """
        return await self.provider.analyze_document_structure(text_content)

    async def classify_paragraph(self, paragraph_text: str, context: str = "") -> Dict[str, Any]:
        """
        Классифицирует отдельный параграф

        Args:
            paragraph_text: Текст параграфа
            context: Контекст (предыдущие параграфы)

        Returns:
            Классификация параграфа
        """
        return await self.provider.classify_paragraph(paragraph_text, context)
