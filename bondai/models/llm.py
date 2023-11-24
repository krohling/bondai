from abc import ABC, abstractmethod
from typing import Dict, List, Callable

class LLM(ABC):

    @abstractmethod
    def supports_streaming() -> bool:
        return False

    @abstractmethod
    def get_completion(
        messages: List[Dict] = [], 
        functions: List[Dict] = [], 
        **kwargs
    ) -> (str, Dict | None):
        pass

    @abstractmethod
    def get_streaming_completion(
        messages: List[Dict] = [], 
        functions: List[Dict] = [], 
        content_stream_callback: Callable[[str], None] | None = None,
        function_stream_callback: Callable[[str], None] | None = None,
        **kwargs
    ) -> (str, Dict | None):
        pass

    @abstractmethod
    def count_tokens(prompt: str) -> int:
        pass

    @abstractmethod
    def get_max_tokens() -> int:
        pass