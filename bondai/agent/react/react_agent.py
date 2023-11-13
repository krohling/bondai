import asyncio
import uuid
from enum import Enum
from termcolor import colored, cprint
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from bondai.agent import Agent, AgentStatus, BudgetExceededException, MaxStepsExceededException
from bondai.util import load_local_resource, format_print_string
from bondai.tools import Tool, ResponseQueryTool
from bondai.prompt import PromptBuilder
from bondai.models import LLM
from bondai.models.openai import (
    OpenAILLM, 
    MODEL_GPT4_0613, 
    MODEL_GPT35_TURBO_0613, 
    get_total_cost
)
from .react_prompt_builder import ReactPromptBuilder

@dataclass
class AgentStep:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    llm_prompt: str
    llm_response: str
    llm_response_function: dict
    tool_output: str
    error_message: str
    success: bool
    step_complete: bool
    agent_complete: bool
    total_cost: float = None
    created_at: datetime = field(default_factory=lambda: datetime.now())
    completed_at: str = None

@dataclass
class AgentResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_description: Optional[str]=None
    task_budget: Optional[float]=None
    max_steps: Optional[int]=None
    output: Optional[str]=None
    error_message: str
    success: bool
    execution_cancelled: bool
    total_cost: float = None
    started_at: datetime = field(default_factory=lambda: datetime.now())
    completed_at: str = None

class ReactAgentEventNames(Enum):
    AGENT_STARTED: str = 'agent_started'
    AGENT_ERROR: str = 'agent_error'
    STEP_STARTED: str = 'step_started'
    STEP_TOOL_SELECTED: str = 'step_tool_selected'
    STEP_COMPLETED: str = 'step_completed'
    AGENT_COMPLETED: str = 'agent_completed'

DEFAULT_MAX_TOOL_RESPONSE_SIZE: int = 2000 #Measured in tokens
DEFAULT_PROMPT_TEMPLATE = load_local_resource(__file__, 'prompt_template.md')

class ReactAgent(Agent):
    """
    An agent that uses the ReAct style of LLM interaction.
    """

    def __init__(self, 
                 persona: str=None,
                 prompt_builder: Optional[PromptBuilder]=None, 
                 llm: LLM=OpenAILLM(MODEL_GPT4_0613), 
                 fallback_llm: LLM=OpenAILLM(MODEL_GPT35_TURBO_0613), 
                 tools: Optional[Tool]=[],
                 max_tool_response_size: int = DEFAULT_MAX_TOOL_RESPONSE_SIZE, 
                 quiet: bool=True
                ):
        """
        Initializes a new instance of the ReactAgent class.

        Args:
            persona (str, optional): The persona to use. Defaults to None.
            prompt_builder (Optional[PromptBuilder], optional): The prompt builder to use. Defaults to None.
            llm (LLM, optional): The LLM to use. Defaults to OpenAILLM(MODEL_GPT4_0613).
            fallback_llm (LLM, optional): The fallback LLM to use. Defaults to OpenAILLM(MODEL_GPT35_TURBO_0613).
            tools (Optional[Tool], optional): The tools to use. Defaults to [].
            max_tool_response_size (int, optional): The maximum size of the tool response. Defaults to DEFAULT_MAX_TOOL_RESPONSE_SIZE.
            quiet (bool, optional): Whether to run the agent in quiet mode. Defaults to True.
        """
        super().__init__(
            prompt_builder=prompt_builder if prompt_builder else ReactPromptBuilder(llm, DEFAULT_PROMPT_TEMPLATE),
            llm=llm,
            tools=tools,
            quiet=quiet,
            allowed_events=[
                ReactAgentEventNames.AGENT_STARTED, 
                ReactAgentEventNames.AGENT_ERROR, 
                ReactAgentEventNames.STEP_STARTED,
                ReactAgentEventNames.STEP_TOOL_SELECTED,
                ReactAgentEventNames.STEP_COMPLETED, 
                ReactAgentEventNames.AGENT_COMPLETED
            ]
        )

        self._persona = persona
        self._execution_cancelled: bool = False
        self._max_tool_response_size: int = max_tool_response_size
        self._task_steps: [AgentStep] = []
        self._response_query_tool: ResponseQueryTool = ResponseQueryTool()
        self._fallback_llm: LLM = fallback_llm
    
    def save_state(self):
        """
        Saves the state of the agent.

        Returns:
            dict: The state of the agent.
        """
        state = super().save_state()
        state['task_steps'] = self._task_steps

        if self._response_query_tool:
            state['response_query_tool'] = self._response_query_tool.save_state()

        return state

    def load_state(self, state):
        """
        Loads the state of the agent.

        Args:
            state (dict): The state of the agent.
        """
        super().load_state(state)
        self._task_steps = state['task_steps']

        if self._response_query_tool and 'response_query_tool' in state:
            self._response_query_tool.load_state(state['response_query_tool'])

    def _run_step(self, task_description: str='') -> AgentStep:
        """
        Runs a step of the agent.

        Args:
            task_description (str, optional): The description of the task. Defaults to ''.

        Returns:
            AgentStep: The step that was run.
        """
        step = AgentStep()
        self._trigger_event(ReactAgentEventNames.STEP_STARTED, step=step)
        
        if len(self._response_query_tool.responses) > 0:
            self._tools.append(self._response_query_tool)

        llm_prompt: str = self._prompt_builder.build_prompt(
            persona=self._persona,
            task_description=task_description, 
            previous_steps=self._task_steps
        )

        messages = [
            {
                'role': 'system',
                'content': llm_prompt
            }
        ]
        llm_response, llm_response_function = self._get_llm_response(messages=messages)
        step.llm_prompt, step.llm_response, step.llm_response_function = llm_prompt, llm_response, llm_response_function

        if not llm_response_function and not self._quiet:
            cprint(f"No function was selected.", 'red')
            cprint(llm_response, 'red')
        
        if llm_response_function:
            selected_tools = [t for t in self._tools if t.name == llm_response_function['name']]
            if len(selected_tools) > 0:
                selected_tool = selected_tools[0]
                self._trigger_event(ReactAgentEventNames.STEP_TOOL_SELECTED, step=step)
                
                try:
                    args = llm_response_function['arguments'] if 'arguments' in llm_response_function else {}
                    
                    if not self._quiet:
                        cprint(f"\n\nUsing the {selected_tool.name} tool", 'yellow', attrs=["bold"])
                        if len(args) > 0:
                            if 'thought' in args:
                                print(colored("Thought:", 'white', attrs=["bold"]), colored(args['thought'], 'white'))

                            cprint("Arguments", 'white', attrs=["bold"])
                            for key, value in args.items():
                                if key != 'thought':
                                    cprint(f"{key}: {format_print_string(str(value))}", 'white')

                    try:
                        tool_output = selected_tool.run(args)
                        if tool_output is dict:
                            if 'output' in tool_output:
                                step.tool_output = tool_output['output']
                            else:
                                raise Exception(f"The tool '{selected_tool.name}' did not return a valid response. A Dictionary response must contain an 'output' key.")
                            
                            if 'agent_complete' in tool_output:
                                step.agent_complete = tool_output['agent_complete']
                        else:
                            step.tool_output = tool_output
                        
                        if step.tool_output:
                            if self._llm.count_tokens(step.tool_output) > self._max_tool_response_size:
                                response_id = self._response_query_tool.add_response(step.tool_output)
                                step.tool_output = f"The result from this tool was greater than {self._max_tool_response_size} tokens and could not be displayed. However, you can use the response_query tool to ask questions about the content of this response. Just use response_id = {response_id}."
                        else:
                            step.tool_output = "This command ran successfully with no output."
                        
                        step.success = True
                        if not self._quiet:
                            print(colored("Output:", 'white', attrs=["bold"]), colored(format_print_string(step.tool_output), 'white'))
                    except Exception as e:
                        # traceback.print_exc()
                        if not self._quiet:
                            cprint(f"An Error occured: {e}", 'red', attrs=["bold"])
                        step.error_message = "An Error occured: " + str(e)
                except Exception as e:
                    if not self._quiet:
                        cprint(f"An Error occured: {e}", 'red', attrs=["bold"])
                    step.error_message = 'An Error occured: The provided arguments were not valid JSON. Valid JSON must ALWAYS BE PROVIDED in the response.'
            else:
                step.error_message = f"An Error occured: The function '{llm_response_function['name']}' does not exist."
                if not self._quiet:
                    cprint(f"No tools found for: {llm_response_function['name']}", 'red', attrs=["bold"])
        else:
            step.error_message="No function was provided", 
        
        return step

    def run(self, task_description: Optional[str]=None, task_budget: Optional[float]=None, max_steps: Optional[int]=None) -> AgentStep:
        """
        Runs the agent's task.

        Args:
            task_description (Optional[str], optional): The description of the task. Defaults to None.
            task_budget (Optional[float], optional): The budget for the task. Defaults to None.
            max_steps (Optional[int], optional): The maximum number of steps for the task. Defaults to None.

        Returns:
            AgentStep: The step that was run.
        """
        if self._status == AgentStatus.RUNNING:
            raise Exception('Execution is already in progress.')
        
        result = AgentResult(
            task_description=task_description, 
            task_budget=task_budget, 
            max_steps=max_steps
        )
        starting_cost = get_total_cost()

        # completed_at: str = None
        
        try:
            self._status = AgentStatus.RUNNING
            self._trigger_event(
                ReactAgentEventNames.AGENT_STARTED, 
                task_description=task_description, 
                task_budget=task_budget, 
                max_steps=max_steps
            )

            step_counter = 0
            while True:
                if self._execution_cancelled:
                    result.execution_cancelled = True
                    break
                step_counter += 1
                step: AgentStep = self._run_step(task_description)
                step.step_complete = True
                step.total_cost = get_total_cost() - starting_cost
                step.completed_at = datetime.now()
                self._task_steps.append(step)
                self._trigger_event(ReactAgentEventNames.STEP_COMPLETED, step=step)
                
                if not self._quiet:
                    print(colored("Total Cost:", 'green', attrs=["bold"]), colored('$' + str(round(total_cost, 2)), 'white'))

                if step.agent_complete:
                    result.output = step.tool_output
                    result.success = True
                    return step

                if task_budget and step.total_cost >= task_budget:
                    raise BudgetExceededException("The budget for this task has been reached without successfully finishing.")
                if max_steps and step_counter >= max_steps:
                    raise MaxStepsExceededException("The maximum number of steps for this task has been reached without successfully finishing.")
        except Exception as e:
            result.error_message = str(e)
            self._trigger_event(ReactAgentEventNames.AGENT_ERROR, error=str(e))
            if asyncio.iscoroutine():
                raise e
        finally:
            self._trigger_event(ReactAgentEventNames.AGENT_COMPLETED)
            self._status = AgentStatus.IDLE
        
        result.total_cost = get_total_cost() - starting_cost
        result.completed_at = datetime.now()
        return result

    async def run_async(self, task_description: str='', task_budget: float=None, max_steps: int=None):
        """
        Runs the agent's task in a separate thread.

        Args:
            task_description (str, optional): The description of the task. Defaults to ''.
            task_budget (float, optional): The budget for the task. Defaults to None.
            max_steps (int, optional): The maximum number of steps for the task. Defaults to None.

        Returns:
            coroutine: The coroutine that runs the task.
        """
        if self._status == AgentStatus.RUNNING or (self._task and not self._task.done()):
            raise Exception('Cannot start agent while it is in a running state.')
        self._task = asyncio.create_task(self.run(task_description, task_budget, max_steps))
        return self._task

    def stop(self, timeout: int=5):
        """
        Gracefully stops the task, with a timeout.

        Args:
            timeout (int, optional): The timeout for stopping the task. Defaults to 5.
        """
        async def _stop_async(self, timeout: int=5):
            self._execution_cancelled = True
            if self._task and not self._task.done():
                try:
                    await asyncio.wait_for(self._task, timeout=timeout)
                except asyncio.TimeoutError:
                    self._task.cancel()
            self._execution_cancelled = False
        
        asyncio.run(_stop_async(timeout))

    def join(self):
        """Blocks until the task completes."""
        async def _join_async(self):
            if self._task:
                await self._task
        asyncio.run(_join_async())
    
    def reset_memory(self):
        """
        Resets the memory of the agent.
        """
        if self._status == AgentStatus.RUNNING:
            raise Exception('Cannot reset memory while agent is in a running state.')
        self._task_steps: [AgentStep] = []
        if self._response_query_tool:
            self._response_query_tool.clear_responses()
