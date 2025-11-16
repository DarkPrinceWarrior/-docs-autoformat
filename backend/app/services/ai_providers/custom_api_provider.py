import aiohttp
from typing import Dict, Any, Optional
import json
from app.services.ai_providers.base import BaseAIProvider


class CustomAPIProvider(BaseAIProvider):
    """Провайдер для пользовательских OpenAI-совместимых API"""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo"
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.api_endpoint = f"{self.base_url}/v1/chat/completions"

    def _get_headers(self) -> Dict[str, str]:
        """Формирует заголовки для запроса"""
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    async def _chat_completion(self, prompt: str, max_tokens: int = 4096) -> str:
        """Отправляет запрос к OpenAI-совместимому API"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.api_endpoint,
                    json=payload,
                    headers=self._get_headers()
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API error: {response.status} - {error_text}")

                    result = await response.json()

                    # Извлекаем ответ из OpenAI-формата
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        raise Exception("Неожиданный формат ответа от API")

            except aiohttp.ClientError as e:
                raise Exception(f"Ошибка подключения к API: {str(e)}")

    async def analyze_document_structure(self, text_content: str) -> Dict[str, Any]:
        """Анализирует структуру документа с использованием пользовательского API"""

        prompt = self._create_structure_prompt(text_content)

        try:
            response_text = await self._chat_completion(prompt, max_tokens=4096)
            json_text = self._extract_json_from_response(response_text)
            structure = json.loads(json_text)

            return structure

        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка парсинга JSON ответа: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка при анализе документа: {str(e)}")

    async def classify_paragraph(self, paragraph_text: str, context: str = "") -> Dict[str, Any]:
        """Классифицирует отдельный параграф с использованием пользовательского API"""

        prompt = self._create_paragraph_prompt(paragraph_text, context)

        try:
            response_text = await self._chat_completion(prompt, max_tokens=512)
            json_text = self._extract_json_from_response(response_text)
            classification = json.loads(json_text)

            return classification

        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка парсинга JSON ответа: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка при классификации параграфа: {str(e)}")
