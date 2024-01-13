---
sidebar_position: 2
---

# Conversational Agents



# ConversationalAgent
**bondai.agents.ConversationalAgent**

The ConversationalAgent in BondAI is inspired by the AutoGen framework as described in the paper [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework](https://arxiv.org/abs/2308.08155). The ConversationalAgent class in BondAI supports single agent interactions with an end user as well as the development of complex Multi-Agent Systems (MAS). MAS are a novel approach to developing LLM applications by employing multiple agents that communicate with each other to solve tasks. These agents are highly customizable, can engage in conversations, and allow for seamless human participation. This multi-agent system, unlike traditional models that rely on a single LLM agent, enables a more diverse and efficient approach to task resolution. It utilizes the strengths of LLMs while addressing their limitations through collaborative agent interactions and human input. This approach is particularly beneficial for a wide range of applications, including coding, mathematics, and online decision-making, by leveraging the power of multiple agents for complex problem-solving and improved reasoning capabilities

```python
class ConversationalAgent(Agent, ConversationMember):
    def __init__(
        self,
        llm: LLM | None = None,
        ...
        enable_conversation_tools: bool = True,
        enable_conversational_content_responses: bool = True,
        enable_exit_conversation: bool = True,
        quiet: bool = True,
    ):

```

## Usage Example

```python
from bondai.agents import ConversationalAgent
from bondai.models.openai import OpenAILLM, OpenAIModelNames

# Initialize the conversational agent
conv_agent = ConversationalAgent(llm=OpenAILLM(OpenAIModelNames.GPT4_0613))

# Configure and run the conversational agent
response = conv_agent.send_message("Hello, how can I assist you today?")
```

## Key Features

- Supports response streaming
- Specializes in conversational interactions.
- Supports asynchronous messaging.
- Extends Agent's capabilities with conversation-specific tools.
- Customizable persona and instructions for interactions (embedded in system prompt).
- Event-driven architecture with additional conversation-specific events.

## Parameters

- Inherits all parameters from [Agent](./react-agent.md).
- **enable_conversation_tools**: Flag to enable conversation-specific tools.
- **enable_conversational_content_responses**: Flag to enable responses based on conversational content.
- **enable_exit_conversation**: Flag to enable the functionality to exit a conversation.
- **quiet**: Controls verbosity, inherited from Agent.

## Methods

- Inherits all methods from [Agent](./react-agent.md).
- **send_message_async(message: str | ConversationMessage, sender_name: str = 'user', group_members: List[ConversationMember] | None = None, group_messages: List[AgentMessage] | None = None, max_attempts: int = 3, require_response: bool = True)**: Sends a message asynchronously. Allows specification of the message, sender name, group members, group messages, maximum send attempts, and whether a response is required.
- **send_message(message: str | ConversationMessage, sender_name: str = 'user', group_members: List[ConversationMember] | None = None, group_messages: List[AgentMessage] | None = None, max_attempts: int = 3, require_response: bool = True)**: Sends a message synchronously and processes the response. Accepts the same parameters as send_message_async.

## Conversational Events

The ConversationalAgent class in BondAI surfaces several key events relevant to conversation handling. These events provide hooks for custom behaviors or additional processing during different stages of a conversation. Here's a list of these events:

- **message_received**: Triggered when a message is received by the agent. This event can be used to execute actions upon the receipt of a new message.
- **message_completed**: Occurs when the agent successfully processes and completes a message. It is useful for post-processing or logging after a message exchange.
- **message_error**: Fired when there is an error in processing a message. This event allows for handling exceptions or errors that occur during message processing.
- **conversation_exited**: Triggered when the agent exits a conversation. This can be used to clean up or reset the agent's state at the end of a conversation.

These events enhance the ConversationalAgent's capabilities, allowing for a more dynamic and responsive conversational flow, and providing opportunities for custom handling and integration in conversational applications.