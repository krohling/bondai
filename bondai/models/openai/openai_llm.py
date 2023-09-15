import os
from bondai.models import LLM
from .openai_wrapper import get_completion, count_tokens, get_max_tokens
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

    def get_completion(self, prompt, system_prompt='', previous_messages=[], functions=[]):
        if MODELS[self.model]['family'] == MODEL_FAMILY_GPT4:
            connection_params = GPT_4_CONNECTION_PARAMS
        else:
            connection_params = GPT_35_CONNECTION_PARAMS
        return get_completion(prompt, system_prompt, previous_messages, functions, self.model, connection_params=connection_params)

    def count_tokens(self, prompt):
        return count_tokens(prompt, self.model)

    def get_max_tokens(self):
        return get_max_tokens(self.model)