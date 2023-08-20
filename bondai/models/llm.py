from abc import ABC, abstractmethod

class LLM(ABC):

    @abstractmethod
    def get_completion(prompt, system_prompt='', previous_messages=[], functions=[]):
        pass

    @abstractmethod
    def count_tokens(prompt):
        pass

    @abstractmethod
    def get_max_tokens():
        pass