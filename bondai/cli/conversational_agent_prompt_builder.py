from bondai.prompt import DefaultPromptBuilder
from bondai.util import load_local_resource

class ConversationalAgentPromptBuilder(DefaultPromptBuilder):
    def __init__(self, llm, tools):
        super(ConversationalAgentPromptBuilder, self).__init__(llm=llm)
        tool_descriptions = ''.join([f"{tool.name}: {tool.description}\n" for tool in tools])
        conversational_agent_prompt_template = load_local_resource(__file__, 'conversational_agent_prompt_template.md')
        self.prompt_template = conversational_agent_prompt_template.replace('{TOOLS}', tool_descriptions)