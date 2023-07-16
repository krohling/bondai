from .steps_formatter import format_previous_steps

class MonitorPromptBuilder():

    def __init__(self, prompt_template):
        self.prompt_template = prompt_template

    def build_prompt(self, task, tools=[], previous_steps=[]):
        if len(previous_steps) > 0:
            str_work = 'This is a list of previous steps that were already completed on this TASK.'
            str_work += format_previous_steps(previous_steps)
        else:
            str_work = '**No previous steps have been completed**'

        tool_names = ','.join(list(map(lambda t: t.name, tools)))
        tool_descriptions = '\n\n'.join(list(map(lambda t: f"**{t.name}**: {t.description}", tools)))

        prompt = self.prompt_template.replace('{TOOL_NAMES}', tool_names)
        prompt = prompt.replace('{TOOL_DESCRIPTIONS}', tool_descriptions)
        prompt = prompt.replace('{WORK}', str_work)
        prompt = prompt.replace('{TASK}', task)
        
        return prompt
