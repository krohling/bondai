from datetime import datetime
from typing import Optional
from bondai.models import LLM
from bondai.prompt import PromptBuilder
from bondai.util import load_local_resource

DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')

class ConversationalPromptBuilder(PromptBuilder):

    def __init__(self, prompt_template: Optional[str]=DEFAULT_PROMPT_TEMPLATE):
        self._prompt_template = prompt_template

    def build_prompt(self, name, role, messages, **kwargs) -> str:
        prompt_vars = {
            'name': name,
            'role': role,
            'datetime': str(datetime.now())
        }
        return self._apply_prompt_template(self._prompt_template, **prompt_vars, **kwargs)
