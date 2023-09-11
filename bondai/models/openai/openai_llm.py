from bondai.models import LLM
from .openai_models import MODEL_NAMES, MODELS, MODEL_TYPE_LLM
from .openai_wrapper import configure_connection, get_completion, count_tokens, get_max_tokens

class OpenAILLM(LLM):
    def __init__(self, model):
        if model not in MODEL_NAMES:
            raise Exception(f"Model {model} is not supported.")
        if MODELS[model]['model_type'] != MODEL_TYPE_LLM:
            raise Exception(f"Model {model} is not an LLM model.")
        self.model = model
        configure_connection()

    def get_completion(self, prompt, system_prompt='', previous_messages=[], functions=[]):
        return get_completion(prompt, system_prompt, previous_messages, functions, self.model)

    def count_tokens(self, prompt):
        return count_tokens(prompt, self.model)

    def get_max_tokens(self):
        return get_max_tokens(self.model)