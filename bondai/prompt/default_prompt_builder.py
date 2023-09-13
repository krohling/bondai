from datetime import datetime
from bondai.prompt import PromptBuilder
from bondai.prompt.steps_formatter import format_previous_steps
from bondai.util import load_local_resource

DEFAULT_PROMPT_TEMPLATE_FILENAME='default_prompt_template.md'
DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, DEFAULT_PROMPT_TEMPLATE_FILENAME)

class DefaultPromptBuilder(PromptBuilder):

    def __init__(self, llm, prompt_template=DEFAULT_PROMPT_TEMPLATE):
        self.llm = llm
        self.prompt_template = prompt_template

    def build_prompt(self, task, tools, previous_steps=[], max_tokens=None):
        if not max_tokens:
            max_tokens = self.llm.get_max_tokens()

        prompt = self.prompt_template.replace('{DATETIME}', str(datetime.now()))
        prompt = prompt.replace('{TASK}', task)

        if len(previous_steps) > 0:
            str_work = 'This is a list of previous steps that you already completed on this TASK.'
            
            remaining_tokens = max_tokens - self.llm.count_tokens(prompt)
            str_work += format_previous_steps(self.llm, previous_steps, remaining_tokens)
        else:
            str_work = '**No previous steps have been completed**'

        prompt = prompt.replace('{WORK}', str_work)
        return prompt
