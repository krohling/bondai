from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from bondai.util import EventMixin
from bondai.tools import Tool
from bondai.prompt import PromptBuilder, DefaultPromptBuilder
from bondai.models import LLM
from bondai.models.openai import (
    OpenAILLM, 
    MODEL_GPT4_0613, 
)

class AgentStatus(Enum):
    RUNNING = 1
    IDLE = 2

class BudgetExceededException(Exception):
    pass

class MaxStepsExceededException(Exception):
    pass

class Agent(EventMixin, ABC):

    def __init__(self, 
                 prompt_builder: PromptBuilder,
                 llm: LLM=OpenAILLM(MODEL_GPT4_0613), 
                 tools: Optional[Tool]=[],
                 quiet: bool=True,
                 allowed_events: [str]=[],
                ):
        super().__init__(allowed_events=allowed_events)
        
        self._status: AgentStatus = AgentStatus.IDLE
        self._prompt_builder = prompt_builder
        self._llm: LLM = llm
        self._tools: [Tool] = tools
        self._quiet: bool = quiet
    
    @property
    def status(self) -> AgentStatus:
        return self._status
    
    def add_tool(self, tool):
        if not any([t.name == tool.name for t in self._tools]):
            self.tools.append(tool)
    
    def remove_tool(self, tool_name):
        self._tools = [t for t in self._tools if t.name != tool_name]
    
    def save_state(self) -> dict:
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot save agent state while it is running.')
        
        state = { 'tools': {} }

        for tool in self._tools:
            state['tools'][tool.name] = tool.save_state()

        return state

    def load_state(self, state: dict):
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot load agent state while it is running.')

        for tool in self._tools:
            if tool.name in state['tools']:
                tool.load_state(state['tools'][tool.name])

    def _get_llm_response(self, prompt: str, previous_messages=[], content_stream_callback: Optional[callable]=None) -> (str, Optional[dict]):
        llm_functions: [dict] = list(map(lambda t: t.get_tool_function(), self._tools))

        if self._llm.supports_streaming() and (any([t.supports_streaming for t in self._tools]) or content_stream_callback):
            def function_stream_callback(function_name, arguments_buffer):
                streaming_tools: [Tool] = [t for t in self._tools if t.name == function_name and t.supports_streaming]
                if len(streaming_tools) > 0:
                    tool: Tool = streaming_tools[0]
                    tool.handle_stream_update(arguments_buffer)
            
            llm_response, llm_response_function = self._llm.get_streaming_completion(
                prompt, 
                functions=llm_functions, 
                previous_messages=previous_messages,
                function_stream_callback=function_stream_callback,
                content_stream_callback=content_stream_callback
            )
        else:
            llm_response, llm_response_function = self._llm.get_completion(
                prompt, 
                functions=llm_functions,
                previous_messages=previous_messages
            )
        
        return llm_response, llm_response_function