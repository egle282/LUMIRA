import google.generativeai as genai
from typing import Type, TypeVar
from pydantic import BaseModel
from .provider import LLMProvider
import json

T = TypeVar('T', bound=BaseModel)

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-pro-latest'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    async def generate_structured_response(self, prompt: str, schema: Type[T]) -> T:
        """
        Calls Gemini and forces it to return JSON matching the Pydantic schema.
        """
        # Append strict instructions to return JSON matching the schema
        schema_json = json.dumps(schema.model_json_schema())
        full_prompt = (
            f"{prompt}\n\n"
            f"IMPORTANT: You must output ONLY valid JSON that strictly conforms to the following schema:\n"
            f"{schema_json}\n"
        )
        
        # Use application/json mime type to enforce JSON format (Supported in Gemini 1.5)
        response = await self.model.generate_content_async(
            full_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Pydantic will validate the JSON string and return the object
        return schema.model_validate_json(response.text)
