from abc import ABC, abstractmethod
from typing import List


class EmbeddingModel(ABC):
    @property
    @abstractmethod
    def max_tokens() -> int:
        pass

    @property
    @abstractmethod
    def embedding_size() -> int:
        pass

    @abstractmethod
    def create_embedding(prompt: str) -> List[float] | List[List[float]]:
        pass

    @abstractmethod
    def count_tokens(prompt: str) -> int:
        pass
