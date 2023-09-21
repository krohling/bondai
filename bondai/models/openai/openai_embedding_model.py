from bondai.models import EmbeddingModel
from .openai_models import MODEL_NAMES, MODELS, MODEL_TYPE_EMBEDDING
from .openai_wrapper import create_embedding, count_tokens, get_max_tokens
from .openai_connection_params import EMBEDDINGS_CONNECTION_PARAMS

class OpenAIEmbeddingModel(EmbeddingModel):
    def __init__(self, model):
        if model not in MODEL_NAMES:
            raise Exception(f"Model {model} is not supported.")
        if MODELS[model]['model_type'] != MODEL_TYPE_EMBEDDING:
            raise Exception(f"Model {model} is not an embedding model.")
        self.model = model

    def create_embedding(self, prompt):
        return create_embedding(prompt, self.model, connection_params=EMBEDDINGS_CONNECTION_PARAMS)

    def count_tokens(self, prompt):
        return count_tokens(prompt, self.model)

    def get_max_tokens(self):
        return get_max_tokens(self.model)