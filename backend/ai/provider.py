from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured_response(self, prompt: str, schema: Type[T]) -> T:
        """
        Generates a structured response from the LLM strictly matching the provided Pydantic schema.
        """
        pass
