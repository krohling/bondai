from abc import ABC, abstractmethod

class EmbeddingModel(ABC):

    @abstractmethod
    def create_embedding(prompt):
        pass

    @abstractmethod
    def count_tokens(prompt):
        pass

    @abstractmethod
    def get_max_tokens():
        pass