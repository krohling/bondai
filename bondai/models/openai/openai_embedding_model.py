from typing import List
from bondai.models import EmbeddingModel
from .openai_models import ModelConfig, OpenAIModelType, OpenAIModelNames
from .openai_wrapper import create_embedding, count_tokens, get_max_tokens
from .openai_connection_params import EMBEDDINGS_CONNECTION_PARAMS


class OpenAIEmbeddingModel(EmbeddingModel):
    def __init__(
        self, model: OpenAIModelNames = OpenAIModelNames.TEXT_EMBEDDING_ADA_002
    ):
        self._model = model.value
        if ModelConfig[self._model]["model_type"] != OpenAIModelType.EMBEDDING:
            raise Exception(f"Model {model} is not an embedding model.")

    @property
    def embedding_size(self) -> int:
        return ModelConfig[self._model]["embedding_size"]

    @property
    def max_tokens(self) -> int:
        return get_max_tokens(self._model)

    def create_embedding(self, prompt: str) -> List[float] | List[List[float]]:
        return create_embedding(
            prompt, self._model, connection_params=EMBEDDINGS_CONNECTION_PARAMS
        )

    def count_tokens(self, prompt: str) -> int:
        return count_tokens(prompt, self._model)
