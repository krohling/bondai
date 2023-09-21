from abc import ABC, abstractmethod

class LLM(ABC):

    @abstractmethod
    def supports_streaming():
        return False

    @abstractmethod
    def get_completion(prompt, system_prompt='', previous_messages=[], functions=[]):
        pass

    @abstractmethod
    def get_streaming_completion(prompt, system_prompt='', previous_messages=[], functions=[], content_stream_callback=None, function_stream_callback=None):
        pass

    @abstractmethod
    def count_tokens(prompt):
        pass

    @abstractmethod
    def get_max_tokens():
        pass