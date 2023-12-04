import uuid
import json
from abc import ABC
from enum import Enum
from typing import Dict, List, Callable
from bondai.util import EventMixin
from bondai.tools import Tool
from bondai.models import LLM
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIModelNames,
)
from .util import (
    AgentStatus,
    AgentException, 
    ContextLengthExceededException,
    count_request_tokens
)

class BaseAgent(EventMixin, ABC):

    def __init__(self, 
                 llm: LLM = OpenAILLM(OpenAIModelNames.GPT4_0613), 
                 tools: List[Tool] = [],
                 quiet: bool = True,
                 allowed_events: List[str] = [],
                ):
        super().__init__(allowed_events=allowed_events)
        
        self._id: str = str(uuid.uuid4())
        self._status: AgentStatus = AgentStatus.IDLE
        self._llm: LLM = llm
        self._tools: List[Tool] = tools
        self._quiet: bool = quiet
    
    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> AgentStatus:
        return self._status
    
    @property
    def tools(self) -> List[Tool]:
        return self._tools
    
    def add_tool(self, tool: Tool):
        if not any([t.name == tool.name for t in self._tools]):
            self.tools.append(tool)
    
    def remove_tool(self, tool_name: str):
        self._tools = [t for t in self._tools if t.name != tool_name]
    
    def save_state(self) -> Dict:
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot save agent state while it is running.')
        
        state = { 'tools': {} }

        for tool in self._tools:
            state['tools'][tool.name] = tool.save_state()

        return state

    def load_state(self, state: Dict):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot load agent state while it is running.')

        for tool in self._tools:
            if tool.name in state['tools']:
                tool.load_state(state['tools'][tool.name])

    def _get_llm_response(self, 
                        messages: List[Dict] = [], 
                        tools: List[Tool] = [],
                        content_stream_callback: Callable[[str], None] | None = None,
                        function_stream_callback: Callable[[str], None] | None = None,
                    ) -> (str | None, Dict | None):
        request_tokens = count_request_tokens(
            llm=self._llm,
            messages=messages,
            tools=tools
        )
        if request_tokens > self._llm.max_tokens:
            raise ContextLengthExceededException(f'Context length ({request_tokens}) exceeds maximum tokens allowed by LLM: {self._llm.max_tokens}')
        
        llm_functions = list(map(lambda t: t.get_tool_function(), tools))

        if self._llm.supports_streaming and (any([t.supports_streaming for t in tools]) or content_stream_callback):
            def tool_function_stream_callback(function_name, arguments_buffer):
                streaming_tools: [Tool] = [t for t in tools if t.name == function_name and t.supports_streaming]
                if len(streaming_tools) > 0:
                    tool: Tool = streaming_tools[0]
                    tool.handle_stream_update(arguments_buffer)
                if function_stream_callback:
                    function_stream_callback(function_name, arguments_buffer)
                
            
            llm_response, llm_response_function = self._llm.get_streaming_completion(
                messages=messages,
                functions=llm_functions, 
                function_stream_callback=tool_function_stream_callback,
                content_stream_callback=content_stream_callback
            )
        else:
            llm_response, llm_response_function = self._llm.get_streaming_completion(
                messages=messages,
                functions=llm_functions, 
                function_stream_callback=function_stream_callback,
                content_stream_callback=content_stream_callback
            )

        return llm_response, llm_response_function

    