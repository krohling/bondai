from abc import ABC, abstractmethod
from typing import List

class EmbeddingModel(ABC):

    @abstractmethod
    def create_embedding(prompt: str) -> List[float] | List[List[float]]:
        pass

    @abstractmethod
    def count_tokens(prompt: str) -> int:
        pass

    @abstractmethod
    def get_max_tokens() -> int:
        pass