---
sidebar_position: 1
---

# ReAct Agents

ReAct Agents in BondAI are based on research findings in the [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/pdf/2210.03629.pdf) paper. The ReAct architecture bridges reasoning and actions in large language models (LLMs) via the use of tools that are able to interact with the Agent's environment. This methodology enables LLMs to generate both reasoning traces and task-specific actions in an intertwined manner, enhancing the interaction between the two. Reasoning traces aid the model in inducing, tracking, and updating action plans and handling exceptions, while the action component allows the model to interface with external sources like knowledge bases for additional information. ReAct demonstrates improved performance in various tasks, notably overcoming issues in chain-of-thought reasoning and outperforming other methods in decision-making benchmarks.

# Agent
**bondai.agents.Agent**

ReAct Agents are implemented using the Agent class in BondAI.

```python
class Agent:
    def __init__(
        self,
        llm: LLM | None = None,
        embedding_model: EmbeddingModel | None = None,
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
        max_tool_retries: int = 3,
        max_tool_response_tokens=2000,
        enable_context_compression: bool = False,
        enable_final_answer_tool: bool = True,
    ):
```

## Usage Example

```python
from bondai.agents import Agent
from bondai.models.openai import OpenAILLM, OpenAIModelNames

# Initialize the agent
agent = Agent(llm=OpenAILLM(OpenAIModelNames.GPT4_0613))

# Add tools and configure the agent
agent.add_tool(custom_tool)

# Run the agent for a specific task
result = agent.run(task="Answer customer queries")

```

## Key Features
- Event-driven architecture.
- Integration with large language models (LLMs).
- Integrated embedding models (semantic search).
- Tool management and execution.
- Context and message handling.
- Memory management.
- Context compression capabilities.

## Parameters

- **llm**: Instance of an LLM implementation (i.e. OpenAI GPT-N)
- **embedding_model**: Embedding model instance for handling embeddings.
- **tools**: List of Tool instances that the agent can use.
- **quiet**: Boolean flag for silent operation. Defaults to 'True'.
- **messages**: List of AgentMessage instances representing the agent's message memory.
- **system_prompt_sections**: List of callables that return sections of the system prompt. These are dynamically injected into the system prompt at runtime.
- **system_prompt_builder**: Callable for building the system prompt.
- **message_prompt_builder**: Callable for formatting messages.
- **memory_manager**: Instance of MemoryManager for memory management.
- **max_context_length**: Maximum allowed context length. This defaults to 95% of the LLM's maximum context size.
- **max_context_pressure_ratio**: Maximum context pressure allowed before context compression occurs. This defaults to 80% of the `max_content_length`.
- **max_tool_retries**: Maximum number of retries for tool execution.
- **max_tool_response_tokens**: Maximum number of tokens allowed for tool outputs. This defaults to 2000.
- **enable_context_compression**: Flag to enable/disable context compression.
- **enable_final_answer_tool**: Flag to include the FinalAnswerTool by default which allows the Agent to exit once it has completed it's task.

## Methods

- **id**: Property returning the unique identifier of the agent. No parameters.
- **status**: Property indicating the current status of the agent. No parameters.
- **tools**: Property listing the tools available to the agent. No parameters.
- **clear_messages**: Clears the agent's message history. No parameters.
- **add_tool(tool: Tool)**: Adds a tool to the agent's toolset.
- **remove_tool(tool_name: str)**: Removes a tool from the agent's toolset based on the tool_name.
- **to_dict**: Converts the agent's state into a dictionary. No parameters.
- **save_state**: Saves the current state of the agent. Optional parameter file_path: str for specifying the file path to save the state.
- **load_state(state: Dict)**: Loads the agent's state from a state dictionary.
- **run(task: str, max_steps: int = None, max_budget: float = None)**: Executes the agent's primary functionality for a task with optional parameters max_steps and max_budget.
- **run_async(task: str, max_steps: int = None, max_budget: float = None)**: Starts the agent's execution in a separate thread for a task with optional parameters max_steps and max_budget.
- **stop(timeout=10)**: Gracefully stops the agent's execution with a timeout duration in seconds.

## Agent Events

- **tool_selected**: Occurs when a tool within the agent's toolkit is selected for use. It allows for actions or logging upon tool activation.
- **tool_error**: Fired when an error occurs during the execution of a tool. This event facilitates error handling and debugging of tool-related issues.
- **tool_completed**: Triggered upon the successful completion of a tool's operation. Useful for post-processing steps or confirmation of task completion.
- **streaming_content_updated**: This is fired as new data chunks arrive from the LLM for a content response. This is very useful for streaming responses to an end user.
- **streaming_function_udpated**: This is fired as new data chunks are receied from the LLM for a function selection. This is allows for tool data logging without waiting for the LLM to finish it's response.