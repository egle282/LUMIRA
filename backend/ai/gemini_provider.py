import json
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from .provider import LLMProvider

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        if not api_key:
            raise ValueError("Gemini API key is required")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def generate_structured_response(self, prompt: str, schema: Type[T]) -> T:
        """Generate a schema-validated JSON response using the supported Google Gen AI SDK."""
        schema_json = json.dumps(schema.model_json_schema())
        full_prompt = (
            f"{prompt}\n\n"
            "Return ONLY valid JSON matching this schema. Do not include Markdown fences.\n"
            f"{schema_json}"
        )
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        if not response.text:
            raise ValueError("Gemini returned an empty response")
        return schema.model_validate_json(response.text)
