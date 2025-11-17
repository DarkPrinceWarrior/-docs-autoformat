"""Unit tests for AI providers."""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.services.ai_providers.factory import AIProviderFactory
from app.services.ai_providers.claude_provider import ClaudeProvider
from app.services.ai_providers.ollama_provider import OllamaProvider
from app.services.ai_providers.custom_api_provider import CustomAPIProvider


class TestAIProviderFactory:
    """Tests for AIProviderFactory."""

    def test_create_claude_provider(self):
        """Test creating Claude provider."""
        with patch('app.services.ai_providers.factory.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'claude'
            mock_settings.CLAUDE_API_KEY = 'test-key'

            provider = AIProviderFactory.create_provider()

            assert isinstance(provider, ClaudeProvider)

    def test_create_ollama_provider(self):
        """Test creating Ollama provider."""
        with patch('app.services.ai_providers.factory.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'ollama'
            mock_settings.OLLAMA_BASE_URL = 'http://localhost:11434'
            mock_settings.OLLAMA_MODEL = 'llama3.1'

            provider = AIProviderFactory.create_provider()

            assert isinstance(provider, OllamaProvider)

    def test_create_custom_provider(self):
        """Test creating Custom API provider."""
        with patch('app.services.ai_providers.factory.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'custom'
            mock_settings.CUSTOM_API_BASE_URL = 'http://localhost:8000'
            mock_settings.CUSTOM_API_KEY = 'test-key'
            mock_settings.CUSTOM_API_MODEL = 'gpt-3.5-turbo'

            provider = AIProviderFactory.create_provider()

            assert isinstance(provider, CustomAPIProvider)

    def test_create_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        with patch('app.services.ai_providers.factory.settings') as mock_settings:
            mock_settings.AI_PROVIDER = 'invalid'

            with pytest.raises(ValueError, match="Неизвестный AI провайдер"):
                AIProviderFactory.create_provider()


class TestClaudeProvider:
    """Tests for ClaudeProvider."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return ClaudeProvider(api_key='test-key')

    @pytest.mark.asyncio
    async def test_analyze_document_structure_success(self, provider):
        """Test successful document analysis."""
        mock_response = Mock()
        mock_response.content = [Mock(text='{"sections": [{"title": "Test", "level": 1}]}')]

        with patch.object(provider.client.messages, 'create', return_value=mock_response):
            result = await provider.analyze_document_structure('Test content')

            assert 'sections' in result
            assert isinstance(result['sections'], list)

    @pytest.mark.asyncio
    async def test_analyze_document_structure_error(self, provider):
        """Test document analysis error handling."""
        with patch.object(
            provider.client.messages,
            'create',
            side_effect=Exception('API Error')
        ):
            with pytest.raises(Exception, match='API Error'):
                await provider.analyze_document_structure('Test content')

    def test_provider_name(self, provider):
        """Test provider name property."""
        assert provider.provider_name == 'claude'


class TestOllamaProvider:
    """Tests for OllamaProvider."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return OllamaProvider(
            base_url='http://localhost:11434',
            model='llama3.1'
        )

    @pytest.mark.asyncio
    async def test_analyze_document_structure_success(self, provider):
        """Test successful document analysis."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'message': {
                'content': '{"sections": [{"title": "Test", "level": 1}]}'
            }
        })

        with patch('aiohttp.ClientSession.post', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
            result = await provider.analyze_document_structure('Test content')

            assert 'sections' in result
            assert isinstance(result['sections'], list)

    @pytest.mark.asyncio
    async def test_analyze_document_structure_http_error(self, provider):
        """Test document analysis HTTP error handling."""
        mock_response = Mock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value='Server Error')

        with patch('aiohttp.ClientSession.post', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
            with pytest.raises(Exception, match='Ollama API error'):
                await provider.analyze_document_structure('Test content')

    def test_provider_name(self, provider):
        """Test provider name property."""
        assert provider.provider_name == 'ollama'


class TestCustomAPIProvider:
    """Tests for CustomAPIProvider."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return CustomAPIProvider(
            base_url='http://localhost:8000',
            api_key='test-key',
            model='gpt-3.5-turbo'
        )

    @pytest.mark.asyncio
    async def test_analyze_document_structure_success(self, provider):
        """Test successful document analysis."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'choices': [{
                'message': {
                    'content': '{"sections": [{"title": "Test", "level": 1}]}'
                }
            }]
        })

        with patch('aiohttp.ClientSession.post', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
            result = await provider.analyze_document_structure('Test content')

            assert 'sections' in result
            assert isinstance(result['sections'], list)

    @pytest.mark.asyncio
    async def test_analyze_document_structure_http_error(self, provider):
        """Test document analysis HTTP error handling."""
        mock_response = Mock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value='Unauthorized')

        with patch('aiohttp.ClientSession.post', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
            with pytest.raises(Exception, match='Custom API error'):
                await provider.analyze_document_structure('Test content')

    def test_provider_name(self, provider):
        """Test provider name property."""
        assert provider.provider_name == 'custom'

    def test_headers_include_auth(self, provider):
        """Test that headers include authorization."""
        headers = provider._get_headers()

        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer test-key'
