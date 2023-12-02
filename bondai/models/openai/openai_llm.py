from typing import Dict, List, Callable
from bondai.models import LLM
from .openai_wrapper import get_streaming_completion, count_tokens, get_max_tokens
from .openai_connection_params import (
    GPT_35_CONNECTION_PARAMS,
    GPT_4_CONNECTION_PARAMS,
)
from .openai_models import (
    ModelConfig, 
    OpenAIModelNames,
    OpenAIModelType,
    OpenAIModelFamilyType
)

class OpenAILLM(LLM):
    def __init__(self, model: OpenAIModelNames):
        self._model = model.value
        if ModelConfig[self._model]['model_type'] != OpenAIModelType.LLM:
            raise Exception(f"Model {self._model} is not an LLM model.")

    @property
    def max_tokens(self) -> int:
        return get_max_tokens(self._model)

    @property
    def supports_streaming(self) -> bool:
        return True

    def get_completion(self, 
                        messages: List[Dict] = [], 
                        functions: List[Dict] = [], 
                        **kwargs
                    ) -> (str, Dict | None):
        if ModelConfig[self._model]['family'] == OpenAIModelFamilyType.GPT4:
            connection_params = GPT_4_CONNECTION_PARAMS
        else:
            connection_params = GPT_35_CONNECTION_PARAMS
        
        return get_streaming_completion(
            messages,
            functions, 
            self._model, 
            connection_params=connection_params,
            **kwargs
        )

    def get_streaming_completion(self, 
                                    messages: List[Dict] = [], 
                                    functions: List[Dict] = [],
                                    content_stream_callback: Callable[[str], None] = None,
                                    function_stream_callback: Callable[[str], None] = None,
                                    **kwargs
                                ) -> (str, Dict | None):
        if ModelConfig[self._model]['family'] == OpenAIModelFamilyType.GPT4:
            connection_params = GPT_4_CONNECTION_PARAMS
        else:
            connection_params = GPT_35_CONNECTION_PARAMS
        
        return get_streaming_completion(
            messages,
            functions, 
            self._model, 
            connection_params=connection_params, 
            content_stream_callback=content_stream_callback,
            function_stream_callback=function_stream_callback,
            **kwargs
        )

    def count_tokens(self, prompt: str) -> int:
        return count_tokens(prompt, self._model)
