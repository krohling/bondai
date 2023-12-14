from bondai.prompt import PromptBuilder


class DefaultPromptBuilder(PromptBuilder):
    def __init__(self, prompt_template: str):
        self._prompt_template: str = prompt_template

    def build_prompt(self, **kwargs) -> str:
        return self._apply_prompt_template(self._prompt_template, **kwargs)
