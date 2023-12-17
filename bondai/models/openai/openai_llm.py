from typing import Dict, List, Callable
from bondai.models import LLM
from bondai.util.caching import LLMCache
from .openai_wrapper import (
    get_streaming_completion,
    get_completion,
    count_tokens,
    get_max_tokens,
)
from .openai_connection_params import (
    OpenAIConnectionParams,
)
from . import default_openai_connection_params as DefaultOpenAIConnectionParams
from .openai_models import (
    ModelConfig,
    OpenAIModelNames,
    OpenAIModelType,
    OpenAIModelFamilyType,
)


class OpenAILLM(LLM):
    def __init__(
        self,
        model: OpenAIModelNames | str,
        connection_params: OpenAIConnectionParams = None,
        cache: LLMCache = None,
    ):
        self._cache = cache

        self._model = model.value if isinstance(model, OpenAIModelNames) else model
        if ModelConfig[self._model]["model_type"] != OpenAIModelType.LLM:
            raise Exception(f"Model {self._model} is not an LLM model.")

        if connection_params:
            self._connection_params = connection_params
        elif ModelConfig[self._model]["family"] == OpenAIModelFamilyType.GPT4:
            self._connection_params = (
                DefaultOpenAIConnectionParams.gpt_4_connection_params
            )
        else:
            self._connection_params = (
                DefaultOpenAIConnectionParams.gpt_35_connection_params
            )

        if not self._connection_params:
            raise Exception(f"Connection parameters not set for model {self._model}.")

    @property
    def max_tokens(self) -> int:
        return get_max_tokens(self._model)

    @property
    def supports_streaming(self) -> bool:
        return True

    def count_tokens(self, prompt: str) -> int:
        return count_tokens(prompt, self._model)

    def get_completion(
        self,
        messages: List[Dict] | None = None,
        functions: List[Dict] | None = None,
        **kwargs,
    ) -> (str, Dict | None):
        if messages is None:
            messages = []
        if functions is None:
            functions = []

        if self._cache:
            input_parameters = {"messages": messages, "functions": functions, **kwargs}
            cache_item = self._cache.get_cache_item(input_parameters=input_parameters)
            if cache_item:
                return cache_item

        result = get_completion(
            connection_params=self._connection_params,
            messages=messages,
            functions=functions,
            model=self._model,
            **kwargs,
        )

        if self._cache:
            self._cache.save_cache_item(
                input_parameters=input_parameters, response=result
            )

        return result

    def get_streaming_completion(
        self,
        messages: List[Dict] | None = None,
        functions: List[Dict] | None = None,
        content_stream_callback: Callable[[str], None] = None,
        function_stream_callback: Callable[[str], None] = None,
        **kwargs,
    ) -> (str, Dict | None):
        if messages is None:
            messages = []
        if functions is None:
            functions = []

        if self._cache:
            input_parameters = {"messages": messages, "functions": functions, **kwargs}
            cache_item = self._cache.get_cache_item(input_parameters=input_parameters)
            if cache_item:
                return cache_item

        result = get_streaming_completion(
            connection_params=self._connection_params,
            messages=messages,
            functions=functions,
            model=self._model,
            content_stream_callback=content_stream_callback,
            function_stream_callback=function_stream_callback,
            **kwargs,
        )

        if self._cache:
            self._cache.save_cache_item(
                input_parameters=input_parameters, response=result
            )

        return result
