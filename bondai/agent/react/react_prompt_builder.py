from datetime import datetime
from typing import Optional
from bondai.models import LLM
from bondai.prompt import PromptBuilder
from bondai.util import load_local_resource
from .util import format_previous_steps

DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')

class ReactPromptBuilder(PromptBuilder):

    def __init__(self, llm: LLM, prompt_template: Optional[str]=DEFAULT_PROMPT_TEMPLATE):
        self._llm = llm
        self._prompt_template = prompt_template

    def build_prompt(self, task_description: str, previous_steps=[], max_tokens: int=None, **kwargs) -> str:
        if not max_tokens:
            max_tokens = self._llm.get_max_tokens()

        prompt_vars = { 'task': task_description, 'datetime': str(datetime.now()) }
        prompt = self._apply_prompt_template(self._prompt_template, **prompt_vars, **kwargs)

        if len(previous_steps) > 0:
            str_work = 'This is a list of previous steps that you already completed on this TASK.'
            remaining_tokens = max_tokens - self._llm.count_tokens(prompt)
            str_work += format_previous_steps(self._llm, previous_steps, remaining_tokens)
        else:
            str_work = '**No previous steps have been completed**'

        return self._apply_prompt_template(prompt, **{ 'work': str_work })
