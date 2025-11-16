from typing import Optional
from app.services.ai_providers.base import BaseAIProvider
from app.services.ai_providers.claude_provider import ClaudeProvider
from app.services.ai_providers.ollama_provider import OllamaProvider
from app.services.ai_providers.custom_api_provider import CustomAPIProvider


class AIProviderFactory:
    """Фабрика для создания AI-провайдеров"""

    @staticmethod
    def create_provider(
        provider_type: str,
        **kwargs
    ) -> BaseAIProvider:
        """
        Создает провайдер указанного типа

        Args:
            provider_type: Тип провайдера ('claude', 'ollama', 'custom')
            **kwargs: Параметры для инициализации провайдера

        Returns:
            Экземпляр AI-провайдера

        Raises:
            ValueError: Если указан неподдерживаемый тип провайдера
        """

        provider_type = provider_type.lower()

        if provider_type == "claude":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("Для Claude провайдера требуется api_key")

            model = kwargs.get("model", "claude-3-5-sonnet-20241022")
            return ClaudeProvider(api_key=api_key, model=model)

        elif provider_type == "ollama":
            base_url = kwargs.get("base_url", "http://localhost:11434")
            model = kwargs.get("model", "llama3.1")
            return OllamaProvider(base_url=base_url, model=model)

        elif provider_type == "custom":
            base_url = kwargs.get("base_url")
            if not base_url:
                raise ValueError("Для custom провайдера требуется base_url")

            api_key = kwargs.get("api_key")  # Опционально
            model = kwargs.get("model", "gpt-3.5-turbo")
            return CustomAPIProvider(
                base_url=base_url,
                api_key=api_key,
                model=model
            )

        else:
            raise ValueError(
                f"Неподдерживаемый тип провайдера: {provider_type}. "
                f"Доступные типы: 'claude', 'ollama', 'custom'"
            )
