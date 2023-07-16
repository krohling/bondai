from datetime import datetime
from .steps_formatter import format_previous_steps

class DefaultPromptBuilder():

    def __init__(self, prompt_template):
        self.prompt_template = prompt_template

    def build_prompt(self, task, tools, previous_steps=[]):
        feedback = ''
        if len(previous_steps) > 0:
            str_work = 'This is a list of previous steps that you already completed on this TASK.'
            str_work += format_previous_steps(previous_steps)
            feedback = previous_steps[-1].monitor_feedback
        else:
            str_work = '**No previous steps have been completed**'


        prompt = self.prompt_template.replace('{WORK}', str_work)
        prompt = prompt.replace('{DATETIME}', str(datetime.now()))
        prompt = prompt.replace('{TASK}', task)
        if feedback:
            prompt = prompt.replace('{FEEDBACK}', feedback)
        
        return prompt
