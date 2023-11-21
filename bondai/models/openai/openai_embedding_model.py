from typing import List
from bondai.models import EmbeddingModel
from .openai_models import MODEL_NAMES, MODELS, MODEL_TYPE_EMBEDDING, MODEL_TEXT_EMBEDDING_ADA_002
from .openai_wrapper import create_embedding, count_tokens, get_max_tokens
from .openai_connection_params import EMBEDDINGS_CONNECTION_PARAMS

class OpenAIEmbeddingModel(EmbeddingModel):
    def __init__(self, model: str = MODEL_TEXT_EMBEDDING_ADA_002):
        if model not in MODEL_NAMES:
            raise Exception(f"Model {model} is not supported.")
        if MODELS[model]['model_type'] != MODEL_TYPE_EMBEDDING:
            raise Exception(f"Model {model} is not an embedding model.")
        self.model = model

    def create_embedding(self, prompt: str) -> List[float] | List[List[float]]:
        return create_embedding(prompt, self.model, connection_params=EMBEDDINGS_CONNECTION_PARAMS)

    def count_tokens(self, prompt: str) -> int:
        return count_tokens(prompt, self.model)

    def get_max_tokens(self) -> int:
        return get_max_tokens(self.model)