import json
import inspect
import traceback
from enum import Enum
from typing import List, Dict, Callable
from bondai.models import LLM
from bondai.tools import Tool
from .messages import AgentMessage


class AgentStatus(Enum):
    RUNNING = 1
    IDLE = 2


class AgentException(Exception):
    pass


class BudgetExceededException(AgentException):
    pass


class MaxStepsExceededException(AgentException):
    pass


class ContextLengthExceededException(AgentException):
    pass


class AgentEventNames(Enum):
    CONTEXT_COMPRESSION_REQUESTED: str = "context_compression_requested"
    TOOL_SELECTED: str = "tool_selected"
    TOOL_ERROR: str = "tool_error"
    TOOL_COMPLETED: str = "tool_completed"
    STREAMING_CONTENT_UPDATED: str = "streaming_content_updated"
    STREAMING_FUNCTION_UPDATED: str = "streaming_function_updated"


def count_request_tokens(
    llm: LLM, messages: List[Dict[str, str]], tools: List[Tool] | None = None
) -> int:
    if tools is None:
        tools = []
    message_tokens = llm.count_tokens(json.dumps(messages))
    functions = list(map(lambda t: t.get_tool_function(), tools))
    functions_tokens = llm.count_tokens(json.dumps(functions))

    return message_tokens + functions_tokens


def execute_tool(
    tool_name: str,
    tools: List[Tool],
    tool_arguments: Dict = {},
):
    selected_tool = next((t for t in tools if t.name == tool_name), None)
    if not selected_tool:
        raise AgentException(
            f"You attempted to use a tool: '{tool_name}'. This tool does not exist."
        )

    try:
        if tool_supports_unpacking(selected_tool.run):
            errors = validate_tool_params(selected_tool.run, tool_arguments)
            if len(errors) > 0:
                raise AgentException(
                    f"The following errors occurred using '{tool_name}': {', '.join(errors)}"
                )
            output = selected_tool.run(**tool_arguments)
        else:
            output = selected_tool.run(tool_arguments)

        if not output or (isinstance(output, str) and len(output.strip()) == 0):
            output = f"Tool '{tool_name}' ran successfully with no output."
        return output
    except Exception as e:
        # print(e)
        # traceback.print_exc()
        raise AgentException(
            f"The following error occurred using '{tool_name}': {str(e)}"
        )


def validate_tool_params(func, params):
    errors = []
    sig = inspect.signature(func)
    func_params = set(sig.parameters)

    # Checking for missing required parameters
    for name, param in sig.parameters.items():
        if (
            param.default is inspect.Parameter.empty
            and name not in params
            and name != "arguments"
        ):
            errors.append(f"Missing required parameter: '{name}'")

    # Checking for extra parameters not in function signature
    for param in params:
        if param not in func_params:
            errors.append(f"Parameter '{param}' is not a valid parameter.")

    return errors


def tool_supports_unpacking(func):
    sig = inspect.signature(func)
    parameters = list(sig.parameters.values())

    return not (len(parameters) == 1 and parameters[0].name == "arguments")


def parse_response_content_message(response: str) -> (str, str):
    parts = response.split(":", 1)
    if len(parts) < 2:
        return None, None
    elif len(parts) > 2:
        recipient_name = parts[0]
        message = ":".join(parts[1:])
    else:
        # The first part is the recipient's names, the second is the message
        recipient_name, message = parts

    # Strip any leading or trailing whitespace from the message
    message = message.strip()
    # Strip any leading or trailing whitespace from the entire recipient string
    recipient_name = recipient_name.strip()
    if " to " in recipient_name:
        recipient_name = recipient_name.split(" to ")[1]

    # Return the list of valid recipient name and the message
    return recipient_name, message


def format_llm_messages(
    system_prompt: str,
    messages: List[AgentMessage],
    message_prompt_builder: Callable[..., str],
) -> List[Dict[str, str]]:
    llm_messages = [{"role": "system", "content": system_prompt}]

    for message in messages:
        content = message_prompt_builder(
            message=message, message_type=message.__class__.__name__
        ).strip()
        if message.role == "function":
            llm_messages.append(
                {"role": message.role, "name": message.tool_name, "content": content}
            )
        else:
            llm_messages.append({"role": message.role, "content": content})

    return llm_messages
