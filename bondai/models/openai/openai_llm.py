from typing import Dict, List, Callable
from bondai.models import LLM
from bondai.util.caching import LLMCache
from .openai_wrapper import get_streaming_completion, get_completion, count_tokens, get_max_tokens
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
    def __init__(self, model: OpenAIModelNames, cache: LLMCache = None):
        self._model = model.value
        self._cache = cache
        if ModelConfig[self._model]['model_type'] != OpenAIModelType.LLM:
            raise Exception(f"Model {self._model} is not an LLM model.")

    @property
    def max_tokens(self) -> int:
        return get_max_tokens(self._model)

    @property
    def supports_streaming(self) -> bool:
        return True
    
    def count_tokens(self, prompt: str) -> int:
        return count_tokens(prompt, self._model)

    def get_completion(self, 
                        messages: List[Dict] | None = None, 
                        functions: List[Dict] | None = None, 
                        **kwargs
                    ) -> (str, Dict | None):
        if messages is None:
            messages = []
        if functions is None:
            functions = []
        
        if ModelConfig[self._model]['family'] == OpenAIModelFamilyType.GPT4:
            connection_params = GPT_4_CONNECTION_PARAMS
        else:
            connection_params = GPT_35_CONNECTION_PARAMS

        if self._cache:
            input_parameters = {
                "messages": messages,
                "functions": functions,
                **kwargs
            }
            cache_item = self._cache.get_cache_item(input_parameters=input_parameters)
            if cache_item:
                print("Cache hit")
                return cache_item

        result = get_completion(
            messages,
            functions, 
            self._model, 
            connection_params=connection_params,
            **kwargs
        )

        if self._cache:
            self._cache.save_cache_item(input_parameters=input_parameters, response=result)
        
        return result

    def get_streaming_completion(self, 
                                    messages: List[Dict] | None = None, 
                                    functions: List[Dict] | None = None,
                                    content_stream_callback: Callable[[str], None] = None,
                                    function_stream_callback: Callable[[str], None] = None,
                                    **kwargs
                                ) -> (str, Dict | None):
        if messages is None:
            messages = []
        if functions is None:
            functions = []
        
        if ModelConfig[self._model]['family'] == OpenAIModelFamilyType.GPT4:
            connection_params = GPT_4_CONNECTION_PARAMS
        else:
            connection_params = GPT_35_CONNECTION_PARAMS
        
        if self._cache:
            input_parameters = {
                "messages": messages,
                "functions": functions,
                **kwargs
            }
            cache_item = self._cache.get_cache_item(input_parameters=input_parameters)
            if cache_item:
                return cache_item

        result = get_streaming_completion(
            messages,
            functions, 
            self._model, 
            connection_params=connection_params, 
            content_stream_callback=content_stream_callback,
            function_stream_callback=function_stream_callback,
            **kwargs
        )

        if self._cache:
            print("Cache hit")
            self._cache.save_cache_item(input_parameters=input_parameters, response=result)
        
        return result
