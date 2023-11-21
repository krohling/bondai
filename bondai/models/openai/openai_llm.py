from typing import Optional
from bondai.models import LLM
from .openai_wrapper import get_streaming_completion, count_tokens, get_max_tokens
from .openai_connection_params import (
    GPT_35_CONNECTION_PARAMS,
    GPT_4_CONNECTION_PARAMS,
)
from .openai_models import (
    MODEL_NAMES, 
    MODELS, 
    MODEL_TYPE_LLM, 
    MODEL_FAMILY_GPT4
)

class OpenAILLM(LLM):
    def __init__(self, model: str):
        if model not in MODEL_NAMES:
            raise Exception(f"Model {model} is not supported.")
        if MODELS[model]['model_type'] != MODEL_TYPE_LLM:
            raise Exception(f"Model {model} is not an LLM model.")
        self._model = model

    def supports_streaming(self) -> bool:
        return True

    def get_completion(self, messages=[], functions=[], **kwargs) -> (str, Optional[dict]):
        if MODELS[self._model]['family'] == MODEL_FAMILY_GPT4:
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

    def get_streaming_completion(self, messages=[], functions=[], content_stream_callback=None, function_stream_callback=None, **kwargs) -> (str, Optional[dict]):
        if MODELS[self._model]['family'] == MODEL_FAMILY_GPT4:
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

    def count_tokens(self, prompt) -> int:
        return count_tokens(prompt, self._model)

    def get_max_tokens(self) -> int:
        return get_max_tokens(self._model)