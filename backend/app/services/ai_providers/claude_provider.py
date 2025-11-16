import anthropic
from typing import Dict, Any
import json
from app.services.ai_providers.base import BaseAIProvider


class ClaudeProvider(BaseAIProvider):
    """Провайдер для Claude API от Anthropic"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    async def analyze_document_structure(self, text_content: str) -> Dict[str, Any]:
        """Анализирует структуру документа с использованием Claude API"""

        prompt = self._create_structure_prompt(text_content)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            json_text = self._extract_json_from_response(response_text)
            structure = json.loads(json_text)

            return structure

        except Exception as e:
            raise Exception(f"Ошибка при анализе документа с Claude API: {str(e)}")

    async def classify_paragraph(self, paragraph_text: str, context: str = "") -> Dict[str, Any]:
        """Классифицирует отдельный параграф с использованием Claude API"""

        prompt = self._create_paragraph_prompt(paragraph_text, context)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            json_text = self._extract_json_from_response(response_text)
            classification = json.loads(json_text)

            return classification

        except Exception as e:
            raise Exception(f"Ошибка при классификации параграфа: {str(e)}")
