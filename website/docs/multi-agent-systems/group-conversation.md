---
sidebar_position: 2
---


# GroupConversation

The GroupConversation class in BondAI facilitates the creation and management of conversations involving multiple agents, inspired by advanced multi-agent system research.


```python
class GroupConversation(EventMixin, Runnable):
    def __init__(
        self,
        conversation_members: List[ConversationMember] | None = None,
        conversation_config: BaseGroupConversationConfig | None = None,
        filter_recipient_messages: bool = False,
    ):
```

## Usage Example

```python
from bondai.agents import ConversationalAgent
from bondai.agents.group_chat import GroupConversation

# Initialize conversation members
members = [ConversationalAgent(...), ConversationalAgent(...)]

# Create a group conversation
group_conversation = GroupConversation(conversation_members=members)

# Conduct a group conversation
group_conversation.send_message("MemberName", "Hello, let's discuss.")
```

## Key Features
- Event-driven architecture.
- Manages multi-agent conversations.
- Supports dynamic interaction among multiple conversation participants.
- Facilitates complex conversational flows and decision-making processes.
- Allows for conversations with both predefined and dynamically determined members.


## Parameters

- **conversation_members**: List of ConversationMember instances (i.e. UserProxy or ConversationalAgent) participating in the conversation.
- **conversation_config**: Configuration settings for managing group conversation dynamics.
- **filter_recipient_messages**: Boolean flag to determine whether the message history shown to each conversation member is inclusive of the entire group conversation or just the messages sent to/from that conversation member.

## Methods

- **id**: Property returning the unique identifier of the group conversation. No parameters.
- **status**: Property indicating the current status of the group conversation. No parameters.
- **members**: Property listing the conversation members participating in the group. No parameters.
- **remove_messages_after(timestamp: datetime, inclusive: bool = True)**: Removes messages from the conversation history that occurred after a specific timestamp.
- **send_message(recipient_name: str, message: str, sender_name: str = USER_MEMBER_NAME, require_response: bool = True)**: Sends a message within the group conversation.
- **reset_memory**: Clears the message history for all conversation members.

## Group Conversation Events

- **message_received**: Triggered when a message is received by a member of the conversation.
- **message_error**: Fired when an error occurs in message processing within the group.
- **message_completed**: Occurs when a message has been successfully processed by a member of the conversation.
- **conversation_exited**: Triggered when a member exits the conversation.
