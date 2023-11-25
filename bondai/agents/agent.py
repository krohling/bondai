import uuid
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

class AgentStatus(Enum):
    RUNNING = 1
    IDLE = 2

class AgentException(Exception):
    pass

class BudgetExceededException(AgentException):
    pass

class MaxStepsExceededException(AgentException):
    pass

class Agent(EventMixin, ABC):

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
                        content_stream_callback: Callable[[str], None] | None = None,
                        function_stream_callback: Callable[[str], None] | None = None,
                    ) -> (str | None, Dict | None):
        llm_functions = list(map(lambda t: t.get_tool_function(), self._tools))

        if self._llm.supports_streaming() and (any([t.supports_streaming for t in self._tools]) or content_stream_callback):
            def tool_function_stream_callback(function_name, arguments_buffer):
                streaming_tools: [Tool] = [t for t in self._tools if t.name == function_name and t.supports_streaming]
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
    
    def _execute_tool(self, tool_name: str, tool_arguments: Dict = {}):
        selected_tool = next((t for t in self._tools if t.name == tool_name), None)
        if not selected_tool:
            raise AgentException(f"You attempted to use a tool: '{tool_name}'. This tool does not exist.")

        try:
            output = selected_tool.run(tool_arguments)
            if not output or (isinstance(output, str) and len(output.strip()) == 0):
                output = f"Tool '{tool_name}' ran successfully with no output."
            return output
        except Exception as e:
            raise AgentException(f"The following error occurred using '{tool_name}': {str(e)}")
