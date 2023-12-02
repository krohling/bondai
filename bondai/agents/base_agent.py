import uuid
import inspect
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
                        content_stream_callback: Callable[[str], None] | None = None,
                        function_stream_callback: Callable[[str], None] | None = None,
                    ) -> (str | None, Dict | None):
        llm_functions = list(map(lambda t: t.get_tool_function(), self._tools))

        if self._llm.supports_streaming and (any([t.supports_streaming for t in self._tools]) or content_stream_callback):
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
            errors = BaseAgent._validate_tool_params(selected_tool.run, tool_arguments)
            if len(errors) > 0:
                raise AgentException(f"The following errors occurred using '{tool_name}': {', '.join(errors)}")

            if BaseAgent._supports_unpacking(selected_tool.run):
                output = selected_tool.run(**tool_arguments)
            else:
                output = selected_tool.run(tool_arguments)
            
            if not output or (isinstance(output, str) and len(output.strip()) == 0):
                output = f"Tool '{tool_name}' ran successfully with no output."
            return output
        except Exception as e:
            raise AgentException(f"The following error occurred using '{tool_name}': {str(e)}")

    def _validate_tool_params(func, params):
        """
        Validates if the provided params dictionary contains all required parameters
        for the given function.

        :param func: The function to validate parameters for.
        :param params: A dictionary of parameters to be passed to the function.
        :return: List of error messages for any missing parameters.
        """
        errors = []
        sig = inspect.signature(func)
        func_params = set(sig.parameters)

        # Checking for missing required parameters
        for name, param in sig.parameters.items():
            if param.default is inspect.Parameter.empty and name not in params and name != 'arguments':
                errors.append(f"Missing required parameter: '{name}'")

        # Checking for extra parameters not in function signature
        for param in params:
            if param not in func_params:
                errors.append(f"Parameter '{param}' is not a valid parameter.")

        return errors
    
    def _supports_unpacking(func):
        """
        Checks if the given method has two parameters, where the first is 'self' 
        and the second is 'arguments'.

        :param func: The method to check.
        :return: True if the method has 'self' and 'arguments' as its parameters, False otherwise.
        """
        sig = inspect.signature(func)
        parameters = list(sig.parameters.values())

        # Check if there are two parameters and they are 'self' and 'arguments'
        return not (len(parameters) == 2 and 
                parameters[0].name == 'self' and 
                parameters[1].name == 'arguments')