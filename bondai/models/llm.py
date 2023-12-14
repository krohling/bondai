from abc import ABC, abstractmethod
from typing import Dict, List, Callable


class LLM(ABC):
    @property
    @abstractmethod
    def max_tokens() -> int:
        pass

    @property
    @abstractmethod
    def supports_streaming() -> bool:
        return False

    @abstractmethod
    def get_completion(
        messages: List[Dict] | None = None,
        functions: List[Dict] | None = None,
        **kwargs
    ) -> (str, Dict | None):
        pass

    @abstractmethod
    def get_streaming_completion(
        messages: List[Dict] | None = None,
        functions: List[Dict] | None = None,
        content_stream_callback: Callable[[str], None] | None = None,
        function_stream_callback: Callable[[str], None] | None = None,
        **kwargs
    ) -> (str, Dict | None):
        pass

    @abstractmethod
    def count_tokens(prompt: str) -> int:
        pass
