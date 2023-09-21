import os
from bondai.models import LLM
from .openai_wrapper import get_streaming_completion, get_completion, count_tokens, get_max_tokens
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
    def __init__(self, model, connection_details={}):
        if model not in MODEL_NAMES:
            raise Exception(f"Model {model} is not supported.")
        if MODELS[model]['model_type'] != MODEL_TYPE_LLM:
            raise Exception(f"Model {model} is not an LLM model.")
        self.model = model

    def supports_streaming(self):
        return True

    def get_completion(self, prompt, system_prompt='', previous_messages=[], functions=[]):
        if MODELS[self.model]['family'] == MODEL_FAMILY_GPT4:
            connection_params = GPT_4_CONNECTION_PARAMS
        else:
            connection_params = GPT_35_CONNECTION_PARAMS
        
        return get_streaming_completion(
            prompt, 
            system_prompt, 
            previous_messages, 
            functions, 
            self.model, 
            connection_params=connection_params)

    def get_streaming_completion(self, prompt, system_prompt='', previous_messages=[], functions=[], content_stream_callback=None, function_stream_callback=None):
        if MODELS[self.model]['family'] == MODEL_FAMILY_GPT4:
            connection_params = GPT_4_CONNECTION_PARAMS
        else:
            connection_params = GPT_35_CONNECTION_PARAMS
        
        return get_streaming_completion(
            prompt, 
            system_prompt, 
            previous_messages, 
            functions, 
            self.model, 
            connection_params=connection_params, 
            content_stream_callback=content_stream_callback,
            function_stream_callback=function_stream_callback)

    def count_tokens(self, prompt):
        return count_tokens(prompt, self.model)

    def get_max_tokens(self):
        return get_max_tokens(self.model)