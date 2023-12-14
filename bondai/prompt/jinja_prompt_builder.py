import platform
from datetime import datetime
from jinja2 import Template
from bondai.prompt import PromptBuilder


class JinjaPromptBuilder(PromptBuilder):
    def __init__(self, prompt_template: str):
        self._prompt_template: str = prompt_template

    def _apply_prompt_template(self, template_string: str, **kwargs) -> str:
        template = Template(template_string)
        return template.render(**kwargs)

    def build_prompt(self, **kwargs) -> str:
        default_vars = {
            "platform": platform.system(),
            "datetime": str(datetime.now()),
        }
        return self._apply_prompt_template(
            self._prompt_template, **default_vars, **kwargs
        )
