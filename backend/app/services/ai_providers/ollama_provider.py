import aiohttp
from typing import Dict, Any
import json
from app.services.ai_providers.base import BaseAIProvider


class OllamaProvider(BaseAIProvider):
    """Провайдер для локальных моделей через Ollama"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.api_endpoint = f"{self.base_url}/api/generate"

    async def _generate(self, prompt: str, max_tokens: int = 4096) -> str:
        """Отправляет запрос к Ollama API"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.3,
            }
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.api_endpoint, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")

                    result = await response.json()
                    return result.get("response", "")

            except aiohttp.ClientError as e:
                raise Exception(f"Ошибка подключения к Ollama: {str(e)}")

    async def analyze_document_structure(self, text_content: str) -> Dict[str, Any]:
        """Анализирует структуру документа с использованием Ollama"""

        prompt = self._create_structure_prompt(text_content)

        try:
            response_text = await self._generate(prompt, max_tokens=4096)
            json_text = self._extract_json_from_response(response_text)
            structure = json.loads(json_text)

            return structure

        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка парсинга JSON ответа от Ollama: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка при анализе документа с Ollama: {str(e)}")

    async def classify_paragraph(self, paragraph_text: str, context: str = "") -> Dict[str, Any]:
        """Классифицирует отдельный параграф с использованием Ollama"""

        prompt = self._create_paragraph_prompt(paragraph_text, context)

        try:
            response_text = await self._generate(prompt, max_tokens=512)
            json_text = self._extract_json_from_response(response_text)
            classification = json.loads(json_text)

            return classification

        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка парсинга JSON ответа от Ollama: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка при классификации параграфа: {str(e)}")
