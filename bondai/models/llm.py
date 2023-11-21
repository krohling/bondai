from abc import ABC, abstractmethod
from typing import List, Callable

class LLM(ABC):

    @abstractmethod
    def supports_streaming() -> bool:
        return False

    @abstractmethod
    def get_completion(
        messages: List[dict] = [], 
        functions: List[dict] = [], 
        **kwargs
    ) -> (str, dict | None):
        pass

    @abstractmethod
    def get_streaming_completion(
        messages: List[dict] = [], 
        functions: List[dict] = [], 
        content_stream_callback: Callable[[str], None] | None = None,
        function_stream_callback: Callable[[str], None] | None = None,
        **kwargs
    ) -> (str, dict | None):
        pass

    @abstractmethod
    def count_tokens(prompt: str) -> int:
        pass

    @abstractmethod
    def get_max_tokens() -> int:
        pass