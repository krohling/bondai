from abc import ABC, abstractmethod

class PromptBuilder(ABC):

    @abstractmethod
    def build_prompt(self, **kwargs):
        pass

    def _apply_prompt_template(prompt_template: str, **kwargs) -> str:
        return prompt_template.format_map(kwargs)