from abc import ABC, abstractmethod

class PromptBuilder(ABC):

    @abstractmethod
    def build_prompt(self, task, tools, previous_steps=[], max_tokens=None):
        pass