import os
import uuid
import traceback
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Tuple, Callable
from bondai.util import EventMixin, Runnable, load_local_resource
from bondai.tools import Tool, ResponseQueryTool
from bondai.models import LLM
from bondai.memory import MemoryManager
from bondai.prompt import JinjaPromptBuilder
from bondai.models.openai import OpenAILLM, OpenAIModelNames, get_total_cost
from .conversation_member import ConversationMember
from .messages import AgentMessage, AgentMessageList, SystemMessage, ToolUsageMessage
from .compression import summarize_conversation, summarize_messages
from .util import (
    AgentStatus,
    AgentEventNames,
    AgentException,
    BudgetExceededException,
    MaxStepsExceededException,
    ContextLengthExceededException,
    count_request_tokens,
    format_llm_messages,
    execute_tool,
)


DEFAULT_MAX_TOOL_RETRIES = 3
DEFAULT_MAX_TOOL_RESPONSE_TOKENS = 2000
DEFAULT_SYSTEM_PROMPT_TEMPLATE = load_local_resource(
    __file__, os.path.join("prompts", "react_agent_system_prompt_template.md")
)
DEFAULT_MESSAGE_PROMPT_TEMPLATE = load_local_resource(
    __file__, os.path.join("prompts", "agent_message_prompt_template.md")
)


class FinalAnswerParameters(BaseModel):
    results: str


class FinalAnswerTool(Tool):
    def __init__(self):
        super().__init__(
            "final_answer",
            "Use the final_answer tool once you have completed your TASK. Provide a highly detailed description of the results of your task in the 'results' parameter.",
            FinalAnswerParameters,
        )

    def run(self, results: str) -> Tuple[str, bool]:
        return results, True


class Agent(EventMixin, Runnable):
    def __init__(
        self,
        llm: LLM | None = None,
        tools: List[Tool] | None = None,
        quiet: bool = True,
        allowed_events: List[str] | None = None,
        messages: List[AgentMessage] | None = None,
        system_prompt_sections: List[Callable[[], str]] | None = None,
        system_prompt_builder: Callable[..., str] = None,
        message_prompt_builder: Callable[..., str] = None,
        memory_manager: MemoryManager | None = None,
        max_context_length: int = None,
        max_context_pressure_ratio: float = 0.8,
        max_tool_retries: int = DEFAULT_MAX_TOOL_RETRIES,
        max_tool_response_tokens=DEFAULT_MAX_TOOL_RESPONSE_TOKENS,
        enable_context_compression: bool = False,
        enable_final_answer_tool: bool = True,
    ):
        Runnable.__init__(self)
        if allowed_events is None:
            allowed_events = [
                AgentEventNames.TOOL_SELECTED,
                AgentEventNames.TOOL_COMPLETED,
                AgentEventNames.TOOL_ERROR,
                AgentEventNames.STREAMING_CONTENT_UPDATED,
                AgentEventNames.STREAMING_FUNCTION_UPDATED,
                AgentEventNames.CONTEXT_COMPRESSION_REQUESTED,
            ]
        EventMixin.__init__(self, allowed_events=allowed_events)

        if llm is None:
            llm = OpenAILLM(OpenAIModelNames.GPT4_0613)
        if tools is None:
            tools = []
        if system_prompt_sections is None:
            system_prompt_sections = []
        if messages is None:
            messages = []

        self._id: str = str(uuid.uuid4())
        self._status: AgentStatus = AgentStatus.IDLE
        self._messages = AgentMessageList(messages=messages)
        self._llm: LLM = llm
        self._tools: List[Tool] = tools
        self._quiet: bool = quiet
        self._system_prompt_sections: List[Callable[[], str]] = system_prompt_sections
        self._system_prompt_builder: Callable[..., str] = system_prompt_builder
        self._message_prompt_builder: Callable[..., str] = message_prompt_builder
        self._memory_manager = memory_manager
        self._max_context_length = (
            max_context_length if max_context_length else (self._llm.max_tokens * 0.95)
        )
        self._max_context_pressure_ratio = max_context_pressure_ratio
        self._max_tool_retries = max_tool_retries
        self._max_tool_response_tokens = max_tool_response_tokens
        self._enable_context_compression = enable_context_compression
        if self._memory_manager:
            self._tools.extend(self._memory_manager.tools)
            self._system_prompt_sections.append(self._memory_manager)
        if self._system_prompt_builder is None:
            self._system_prompt_builder = JinjaPromptBuilder(
                DEFAULT_SYSTEM_PROMPT_TEMPLATE
            )
        if self._message_prompt_builder is None:
            self._message_prompt_builder = JinjaPromptBuilder(
                DEFAULT_MESSAGE_PROMPT_TEMPLATE
            )
        if enable_final_answer_tool:
            self._tools.append(FinalAnswerTool())

    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> AgentStatus:
        return self._status

    @property
    def tools(self) -> List[Tool]:
        return self._tools

    def clear_messages(self):
        if self._status == AgentStatus.RUNNING:
            raise AgentException(
                "Cannot reset memory while agent is in a running state."
            )
        self._messages.clear()

    def add_tool(self, tool: Tool):
        if not any([t.name == tool.name for t in self._tools]):
            self.tools.append(tool)

    def remove_tool(self, tool_name: str):
        self._tools = [t for t in self._tools if t.name != tool_name]

    def to_dict(self) -> Dict:
        return {"id": self.id, "tools": [t.name for t in self._tools]}

    def save_state(self) -> Dict:
        if self._status == AgentStatus.RUNNING:
            raise AgentException("Cannot save agent state while it is running.")

        state = {"tools": {}}

        for tool in self._tools:
            state["tools"][tool.name] = tool.save_state()

        return state

    def load_state(self, state: Dict):
        if self._status == AgentStatus.RUNNING:
            raise AgentException("Cannot load agent state while it is running.")

        for tool in self._tools:
            if tool.name in state["tools"]:
                tool.load_state(state["tools"][tool.name])

    def _is_context_pressure_too_high(
        self,
        llm_messages: List[Dict[str, str]],
        tools: List[Tool] | None = None,
    ) -> float:
        if tools is None:
            tools = []
        context_pressure_ratio = float(
            count_request_tokens(self._llm, llm_messages, tools)
        ) / float(self._max_context_length)
        return context_pressure_ratio > self._max_context_pressure_ratio

    def _get_llm_response(
        self,
        messages: List[Dict] | None = None,
        tools: List[Tool] | None = None,
        content_stream_callback: Callable[[str], None] | None = None,
        function_stream_callback: Callable[[str], None] | None = None,
    ) -> (str | None, Dict | None):
        if messages is None:
            messages = []
        if tools is None:
            tools = []

        request_tokens = count_request_tokens(
            llm=self._llm, messages=messages, tools=tools
        )
        if request_tokens > self._llm.max_tokens:
            raise ContextLengthExceededException(
                f"Context length ({request_tokens}) exceeds maximum tokens allowed by LLM: {self._llm.max_tokens}"
            )

        llm_functions = list(map(lambda t: t.get_tool_function(), tools))

        if (
            self._llm.supports_streaming
        ):  # and (any([t.supports_streaming for t in tools]) or content_stream_callback):

            def _function_stream_callback(function_name, arguments_buffer):
                streaming_tools: [Tool] = [
                    t for t in tools if t.name == function_name and t.supports_streaming
                ]
                if len(streaming_tools) > 0:
                    tool: Tool = streaming_tools[0]
                    tool.handle_stream_update(arguments_buffer)
                if function_stream_callback:
                    function_stream_callback(function_name, arguments_buffer)
                self._trigger_event(
                    AgentEventNames.STREAMING_FUNCTION_UPDATED,
                    self,
                    function_name,
                    arguments_buffer,
                )

            def _content_stream_callback(content_buffer):
                if content_stream_callback:
                    content_stream_callback(content_buffer)
                self._trigger_event(
                    AgentEventNames.STREAMING_CONTENT_UPDATED, self, content_buffer
                )

            llm_response, llm_response_function = self._llm.get_streaming_completion(
                messages=messages,
                functions=llm_functions,
                function_stream_callback=_function_stream_callback,
                content_stream_callback=_content_stream_callback,
            )
        else:
            llm_response, llm_response_function = self._llm.get_completion(
                messages=messages,
                functions=llm_functions,
                # function_stream_callback=function_stream_callback,
                # content_stream_callback=content_stream_callback
            )

        return llm_response, llm_response_function

    def run(
        self,
        task: str,
        max_steps: int = None,
        max_budget: float = None,
    ) -> ToolUsageMessage | str:
        if self._status == AgentStatus.RUNNING:
            raise AgentException("Cannot start agent while it is in a running state.")
        self._status = AgentStatus.RUNNING
        try:
            return self._run_tool_loop(
                tools=self._tools,
                task=task,
                starting_cost=get_total_cost(),
                max_budget=max_budget,
                max_steps=max_steps,
            )
        finally:
            self._status = AgentStatus.IDLE

    def run_async(
        self,
        task: str,
        max_steps: int = None,
        max_budget: float = None,
    ):
        """Runs the agent's task in a separate thread."""
        if self._status == AgentStatus.RUNNING:
            raise AgentException("Cannot start agent while it is in a running state.")

        args = (task, max_steps, max_budget)
        self._start_execution_thread(target=self.run, args=args)

    def stop(self, timeout=10):
        """Gracefully stops the thread, with a timeout."""
        self._force_stop = True
        for tool in self._tools:
            tool.stop()

        super().stop(timeout=timeout)

    def _run_tool_loop(
        self,
        tools: List[Tool],
        starting_cost: float,
        max_budget: float = None,
        max_steps: int = None,
        max_tool_retries: int = None,
        task: str | None = None,
        prompt_vars: Dict | None = None,
        return_conversational_responses: bool = False,
        retain_tool_messages_in_context: bool = True,
        addition_context_messages: List[AgentMessage] | None = None,
        conversation_members: List[ConversationMember] | None = None,
        content_stream_callback: Callable[[str], None] | None = None,
        function_stream_callback: Callable[[str], None] | None = None,
    ) -> ToolUsageMessage | str:
        if addition_context_messages is None:
            addition_context_messages = []
        if conversation_members is None:
            conversation_members = []
        if max_tool_retries is None:
            max_tool_retries = self._max_tool_retries

        error_count = 0
        step_count = 0
        last_error_message = None
        local_messages = []
        self._force_stop = False
        response_query_tool = ResponseQueryTool()

        def append_message(message):
            if isinstance(message, SystemMessage):
                system_messages = [
                    m for m in local_messages if not isinstance(m, SystemMessage)
                ]
                for m in system_messages:
                    local_messages.remove(m)

            local_messages.append(message)
            if retain_tool_messages_in_context:
                self._messages.add(message)
                if self._memory_manager and self._memory_manager.conversation_memory:
                    self._memory_manager.conversation_memory.add(message)

        while not self._force_stop:
            step_count += 1
            if max_budget and get_total_cost() - starting_cost > max_budget:
                raise BudgetExceededException()
            if max_steps and step_count > max_steps:
                raise MaxStepsExceededException()

            if (
                len(response_query_tool.responses) > 0
                and response_query_tool not in tools
            ):
                tools.append(response_query_tool)

            if self._enable_context_compression:
                self._compress_llm_context(
                    tools=tools,
                    last_error_message=last_error_message,
                    conversation_members=conversation_members,
                    additional_context_messages=addition_context_messages
                    + local_messages,
                    prompt_vars=prompt_vars,
                )

            llm_context = self._build_llm_context(
                messages=AgentMessageList(
                    self._messages + addition_context_messages + local_messages
                ),
                tools=tools,
                task=task,
                last_error_message=last_error_message,
                conversation_members=conversation_members,
                prompt_vars=prompt_vars,
            )

            llm_response_content, llm_response_function = self._get_llm_response(
                messages=llm_context,
                tools=tools,
                content_stream_callback=content_stream_callback,
                function_stream_callback=function_stream_callback,
            )
            # print(llm_response_content)

            last_error_message = None
            if llm_response_function and any(
                [
                    m.name == llm_response_function.get("tool_name")
                    for m in conversation_members
                ]
            ):
                message = f"""MessageSendFailure: You attempted to send a message to {llm_response_function.get('tool_name')} but this message failed.
                To send a message to {llm_response_function.get('tool_name')} you must use the 'send_message' tool or use this format in your response:

                ```
                {llm_response_function.get('tool_name')}: Include your message here.)
                ```
                """
                append_message(SystemMessage(message=message))
            if llm_response_function:
                tool_message = ToolUsageMessage(
                    tool_name=llm_response_function["name"],
                    tool_arguments=llm_response_function.get("arguments") or {},
                )
                self._trigger_event(AgentEventNames.TOOL_SELECTED, self, tool_message)
                self._handle_llm_function(tool_message=tool_message, tools=tools)

                if (
                    isinstance(tool_message.tool_output, str)
                    and self._llm.count_tokens(tool_message.tool_output)
                    > self._max_tool_response_tokens
                ):
                    response_id = response_query_tool.add_response(
                        tool_message.tool_output
                    )
                    tool_message.tool_output = f"The result from this tool was greater than {self._max_tool_response_tokens} tokens and could not be displayed. However, you can use the response_query tool to ask questions about the content of this response. Just use response_id = {response_id}."

                append_message(tool_message)
                if tool_message.success:
                    error_count = 0
                    self._trigger_event(
                        AgentEventNames.TOOL_COMPLETED, self, tool_message
                    )
                    if tool_message.agent_halted:
                        return tool_message
                else:
                    error_count += 1
                    last_error_message = str(tool_message.error)
                    message = "ToolUsageError: Your last tool usage failed and MUST BE CORRECTED. If this error is not corrected you will not be able to proceed."
                    append_message(SystemMessage(message=message))
                    self._trigger_event(AgentEventNames.TOOL_ERROR, self, tool_message)
                    if error_count >= max_tool_retries:
                        return tool_message
            elif llm_response_content and return_conversational_responses:
                return llm_response_content
            else:
                error_count += 1
                message = "InvalidResponseError: The response does not conform to the required format. A function selection was expected, but none was provided."
                append_message(SystemMessage(message=message))
                if error_count >= max_tool_retries:
                    raise AgentException(message)

        if self._force_stop:
            self._force_stop = False
            raise AgentException("Agent was forcibly stopped.")

    def _build_llm_context(
        self,
        messages: AgentMessageList,
        tools: List[Tool] | None = None,
        task: str | None = None,
        last_error_message: str | None = None,
        conversation_members: List[ConversationMember] | None = None,
        truncate_context: bool = True,
        prompt_vars: Dict | None = None,
    ) -> (str | None, Dict | None):
        if tools is None:
            tools = []
        if conversation_members is None:
            conversation_members = []
        if prompt_vars is None:
            prompt_vars = {}

        prompt_sections = []
        for s in self._system_prompt_sections:
            if callable(s):
                prompt_sections.append(s())
            else:
                prompt_sections.append(s)

        system_prompt: str = self._system_prompt_builder(
            conversation_members=conversation_members,
            tools=tools,
            task=task,
            prompt_sections=prompt_sections,
            error_message=last_error_message,
            **prompt_vars,
        )

        # print(system_prompt)
        llm_context = format_llm_messages(
            system_prompt, messages, self._message_prompt_builder
        )

        if truncate_context:
            reduced_messages = AgentMessageList(messages)
            while (
                self._is_context_pressure_too_high(llm_context, tools)
                and len(reduced_messages) > 0
            ):
                reduced_messages.remove(reduced_messages[0])
                llm_context = format_llm_messages(
                    system_prompt, reduced_messages, self._message_prompt_builder
                )

        return llm_context

    def _compress_llm_context(
        self,
        tools: List[Tool] | None = None,
        last_error_message: str | None = None,
        conversation_members: List[ConversationMember] | None = None,
        additional_context_messages: List[AgentMessage] | None = None,
        prompt_vars: Dict | None = None,
    ) -> List[AgentMessage]:
        if tools is None:
            tools = []
        if conversation_members is None:
            conversation_members = []
        if additional_context_messages is None:
            additional_context_messages = []

        all_context_messages = AgentMessageList(
            self._messages + additional_context_messages
        )

        llm_context = self._build_llm_context(
            messages=all_context_messages,
            tools=tools,
            last_error_message=last_error_message,
            conversation_members=conversation_members,
            truncate_context=False,
            prompt_vars=prompt_vars,
        )

        if self._is_context_pressure_too_high(llm_context, tools):
            # Try summarizing individual messages
            # TODO: Give the agent an opportunity to save information to Archival database

            summarize_messages(
                llm=self._llm,
                messages=self._messages[:-1],
                message_prompt_builder=self._message_prompt_builder,
            )

            llm_context = self._build_llm_context(
                messages=all_context_messages,
                tools=tools,
                last_error_message=last_error_message,
                conversation_members=conversation_members,
                truncate_context=False,
                prompt_vars=prompt_vars,
            )

            if self._is_context_pressure_too_high(llm_context, tools):
                # Try summarizing the entire conversation

                last_message = self._messages[-1]
                summary_message = summarize_conversation(
                    llm=self._llm,
                    messages=self._messages[:-1],
                    message_prompt_builder=self._message_prompt_builder,
                )
                self._messages.clear()
                self._messages.add(summary_message)
                self._messages.add(last_message)

                all_context_messages = AgentMessageList(
                    self._messages + additional_context_messages
                )
                llm_context = self._build_llm_context(
                    messages=all_context_messages,
                    tools=tools,
                    last_error_message=last_error_message,
                    conversation_members=conversation_members,
                    truncate_context=False,
                    prompt_vars=prompt_vars,
                )

                if self._is_context_pressure_too_high(llm_context, tools):
                    # Fire a message for group conversation compression
                    self._trigger_event(
                        AgentEventNames.CONTEXT_COMPRESSION_REQUESTED, self
                    )

                    llm_context = self._build_llm_context(
                        messages=all_context_messages,
                        tools=tools,
                        last_error_message=last_error_message,
                        conversation_members=conversation_members,
                        truncate_context=False,
                        prompt_vars=prompt_vars,
                    )

                    if self._is_context_pressure_too_high(llm_context, tools):
                        print(
                            "Warning: Context compression failed to relieve pressure."
                        )

    def _handle_llm_function(self, tool_message: ToolUsageMessage, tools: List[Tool]):
        tool_starting_cost = get_total_cost()

        try:
            tool_output = execute_tool(
                tool_name=tool_message.tool_name,
                tool_arguments=tool_message.tool_arguments,
                tools=tools,
            )

            agent_halted = False
            if isinstance(tool_output, tuple):
                tool_output, agent_halted = tool_output

            tool_message.agent_halted = agent_halted
            tool_message.tool_output = tool_output
            tool_message.success = True
        except Exception as e:
            # traceback.print_exc()
            tool_message.error = e

        tool_message.completed_at = datetime.now()
        tool_message.cost = get_total_cost() - tool_starting_cost
