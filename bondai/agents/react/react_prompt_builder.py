from typing import List
from bondai.models import LLM
from bondai.prompt import JinjaPromptBuilder
from bondai.util import load_local_resource
from .react_agent import AgentStep

DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')

class ReactPromptBuilder(JinjaPromptBuilder):

    def __init__(self, llm: LLM, prompt_template: str = DEFAULT_PROMPT_TEMPLATE):
        self._llm = llm
        super().__init__(prompt_template=prompt_template)

    def build_prompt(self, 
                    persona: str | None = None, 
                    task_description: str | None = None, 
                    previous_steps: List[AgentStep] = [], 
                    max_tokens: int | None = None, 
                    **kwargs
                ) -> str:
        if not max_tokens:
            max_tokens = self._llm.get_max_tokens()

        # Start with the full previous steps and remove from the beginning if necessary
        retained_steps = previous_steps[:]
        prompt = super().build_prompt(
            persona=persona,
            task_description=task_description,
            previous_steps=retained_steps,
            **kwargs
        )

        # Check the prompt size and remove steps from the beginning until it fits
        prompt_size = self._llm.count_tokens(prompt)
        while prompt_size > max_tokens:
            if not retained_steps:
                # If there are no previous steps left to remove and the prompt is still too large, raise an exception
                raise ValueError("The prompt is too large and cannot be trimmed down because the previous_steps array is empty.")
            retained_steps.pop(0)  # Remove the oldest step
            prompt = super().build_prompt(
                persona=persona,
                task_description=task_description,
                previous_steps=retained_steps,
                **kwargs
            )
            prompt_size = self._llm.count_tokens(prompt)

        return prompt
