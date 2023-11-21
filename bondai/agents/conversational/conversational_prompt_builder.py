from typing import List
from bondai.prompt import JinjaPromptBuilder
from bondai.util import load_local_resource
from .conversation_member import ConversationMember

DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')

class ConversationalPromptBuilder(JinjaPromptBuilder):

    def __init__(self, prompt_template: str = DEFAULT_PROMPT_TEMPLATE):
        super().__init__(prompt_template=prompt_template)

    def build_prompt(self, 
                    name: str, 
                    persona: str | None = None, 
                    conversation_members: List[ConversationMember] = [], 
                    error_message: str | None = None, 
                    **kwargs
                ) -> str:
        return super().build_prompt(
            name=name,
            persona=persona,
            conversation_members=conversation_members,
            error_message=error_message,
            **kwargs
        )