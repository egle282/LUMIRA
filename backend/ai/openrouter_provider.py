import json
from typing import Type, TypeVar
from pydantic import BaseModel
from openai import AsyncOpenAI
from .provider import LLMProvider

T = TypeVar('T', bound=BaseModel)

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = 'google/gemma-7b-it:free'):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model_name

    async def generate_structured_response(self, prompt: str, schema: Type[T]) -> T:
        """
        Calls OpenRouter and forces it to return JSON matching the Pydantic schema.
        We instruct the model via system prompt and use response_format.
        """
        schema_json = json.dumps(schema.model_json_schema())
        
        system_prompt = (
            f"You are a helpful assistant. You must reply strictly in valid JSON format.\n"
            f"Your output MUST exactly match this JSON schema:\n{schema_json}"
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        json_string = response.choices[0].message.content
        return schema.model_validate_json(json_string)
