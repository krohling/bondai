import asyncio
import uuid
import json
from enum import Enum
from datetime import datetime
from typing import List
from dataclasses import dataclass, field
from bondai.util import load_local_resource
from bondai.tools import Tool, ResponseQueryTool
from bondai.prompt import PromptBuilder
from bondai.models import LLM
from bondai.agents import (
    Agent, 
    AgentStatus, 
    AgentException,
    BudgetExceededException, 
    MaxStepsExceededException
)
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIModelNames,
    get_total_cost
)
from .react_prompt_builder import ReactPromptBuilder

@dataclass
class AgentStep:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    llm_prompt: str | None = field(default=None)
    llm_response: str | None = field(default=None)
    llm_response_function: dict | None = field(default=None)
    tool_output: str | None = field(default=None)
    error_message: str | None = field(default=None)
    success: bool = field(default=False)
    step_complete: bool = field(default=False)
    agent_complete: bool = field(default=False)
    total_cost: float | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now())
    completed_at: datetime | None = field(default=None)

@dataclass
class AgentResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_description: str | None = field(default=None)
    task_budget: float | None = field(default=None)
    max_steps: int | None = field(default=None)
    output: str | None = field(default=None)
    error_message: str | None = field(default=None)
    success: bool = field(default=False)
    execution_cancelled: bool = field(default=False)
    total_cost: float | None = field(default=None)
    started_at: datetime = field(default_factory=lambda: datetime.now())
    completed_at: datetime | None = field(default=None)

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
                    persona: str | None = None,
                    system_prompt_builder: PromptBuilder | None = None, 
                    llm: LLM = OpenAILLM(OpenAIModelNames.GPT4_0613), 
                    fallback_llm: LLM = OpenAILLM(OpenAIModelNames.GPT35_TURBO_0613), 
                    tools: List[Tool] = [],
                    max_tool_response_size: int = DEFAULT_MAX_TOOL_RESPONSE_SIZE, 
                    quiet: bool = True
                ):
        super().__init__(
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
        self._task_steps: List[AgentStep] = []
        self._response_query_tool: ResponseQueryTool = ResponseQueryTool()
        self._fallback_llm: LLM = fallback_llm

        if not system_prompt_builder:
            system_prompt_builder = ReactPromptBuilder(DEFAULT_PROMPT_TEMPLATE)
        self._system_prompt_builder: PromptBuilder = system_prompt_builder
    
    def save_state(self) -> dict:
        state = super().save_state()
        state['task_steps'] = self._task_steps

        if self._response_query_tool:
            state['response_query_tool'] = self._response_query_tool.save_state()

        return state

    def load_state(self, state : dict):
        super().load_state(state)
        self._task_steps = state['task_steps']

        if self._response_query_tool and 'response_query_tool' in state:
            self._response_query_tool.load_state(state['response_query_tool'])

    def _run_step(self, step: AgentStep):
        if len(self._response_query_tool._responses) > 0:
            self._tools.append(self._response_query_tool)

        step.llm_prompt = self._system_prompt_builder.build_prompt(
            persona=self._persona,
            task_description=step.task_description, 
            previous_steps=self._task_steps
        )

        messages = [ { 'role': 'system', 'content': step.llm_prompt } ]
        step.llm_response, step.llm_response_function = self._get_llm_response(messages=messages)
        if not step.llm_response_function:
            raise AgentException('An Error occurred: A function must be provided and no function was present in the last response.')
        
        try:
            arguments = json.loads(step.llm_response_function['arguments'] if 'arguments' in step.llm_response_function else {})
        except json.decoder.JSONDecodeError:
            raise AgentException(f"Invalid arguments were used for the function: '{step.llm_response_function['name']}'")
        
        self._trigger_event(ReactAgentEventNames.STEP_TOOL_SELECTED, step=step)
        step.tool_output = self._execute_tool(step.llm_response_function['name'], arguments)
        
        if step.tool_output:
            if isinstance(step.tool_output, tuple):
                step.tool_output, step.agent_complete = step.tool_output
            
            if self._llm.count_tokens(step.tool_output) > self._max_tool_response_size:
                response_id = self._response_query_tool.add_response(step.tool_output)
                step.tool_output = f"The result from this tool was greater than {self._max_tool_response_size} tokens and could not be displayed. However, you can use the response_query tool to ask questions about the content of this response. Just use response_id = {response_id}."
        else:
            step.tool_output = "This command ran successfully with no output."

    def run(self, 
            task_description: str | None = None, 
            task_budget: float | None = None, 
            max_steps: int | None = None
        ) -> AgentResult:
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Execution is already in progress.')
        
        agent_result = AgentResult(
            task_description=task_description, 
            task_budget=task_budget, 
            max_steps=max_steps
        )
        starting_cost = get_total_cost()
        
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
                    agent_result.execution_cancelled = True
                    break
                step_counter += 1

                agent_step = AgentStep(task_description=task_description)
                self._task_steps.append(agent_step)
                self._trigger_event(ReactAgentEventNames.STEP_STARTED, step=agent_step)

                try:
                    self._run_step(agent_step)
                    agent_step.success = True
                except Exception as e:
                    agent_step.success = False
                    agent_step.error_message = str(e)
                finally:
                    agent_step.step_complete = True
                    agent_step.total_cost = get_total_cost() - starting_cost
                    agent_step.completed_at = datetime.now()

                self._trigger_event(ReactAgentEventNames.STEP_COMPLETED, step=agent_step)

                if agent_step.agent_complete:
                    agent_result.output = agent_step.tool_output
                    agent_result.success = True
                    return agent_step

                if task_budget and agent_step.total_cost >= task_budget:
                    raise BudgetExceededException("The budget for this task has been reached without successfully finishing.")
                if max_steps and step_counter >= max_steps:
                    raise MaxStepsExceededException("The maximum number of steps for this task has been reached without successfully finishing.")
        except Exception as e:
            agent_result.error_message = str(e)
            self._trigger_event(ReactAgentEventNames.AGENT_ERROR, error=str(e))
            if asyncio.iscoroutine():
                raise e
        finally:
            self._trigger_event(ReactAgentEventNames.AGENT_COMPLETED)
            self._status = AgentStatus.IDLE
        
        agent_result.total_cost = get_total_cost() - starting_cost
        agent_result.completed_at = datetime.now()
        return agent_result

    async def run_async(self, 
                        task_description: str | None = None, 
                        task_budget: float | None = None, 
                        max_steps: int | None = None
                    ):
        if self._status == AgentStatus.RUNNING or (self._task and not self._task.done()):
            raise AgentException('Cannot start agent while it is in a running state.')
        self._task = asyncio.create_task(self.run(task_description, task_budget, max_steps))
        return self._task

    def stop(self, timeout: int=5):
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
        async def _join_async(self):
            if self._task:
                await self._task
        asyncio.run(_join_async())
    
    def reset_memory(self):
        if self._status == AgentStatus.RUNNING:
            raise AgentException('Cannot reset memory while agent is in a running state.')
        self._task_steps: [AgentStep] = []
        if self._response_query_tool:
            self._response_query_tool.clear_responses()
