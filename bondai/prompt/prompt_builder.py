from abc import ABC, abstractmethod
from typing import Dict, Any


class PromptBuilder(ABC):
    def __call__(self, **kwargs: Dict[str, Any]) -> str:
        return self.build_prompt(**kwargs)

    @abstractmethod
    def build_prompt(self, **kwargs: Dict[str, Any]) -> str:
        pass

    def _apply_prompt_template(prompt_template: str, **kwargs) -> str:
        return prompt_template.format_map(kwargs)
