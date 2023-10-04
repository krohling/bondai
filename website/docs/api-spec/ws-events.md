---
sidebar_position: 6
---

# WebSocket Events

The BondAI API server will host a WebSocket endpoint on the specified server port (default: 2663). The following events are supported.

**Agent Message**

This event is sent when the Agent wants to communicate with the user.

```json
{
    "event": "agent_message",
    "data": {
        "message": "How can I help you today?"
    }
}
```

**User Message**

To communicate back to the Agent on the user's behalf just send a `user_message` event.

```json
{
    "event": "user_message",
    "data": {
        "message": "I want you to write a story about unicorns."
    }
}
```

**Agent Started**

This event is sent when the Agent starts working on a task. This can be triggered by calling the [Start Agent](./start-agent) API.

```json
{ "event": "agent_started" }
```


**Step Completed**

This event is sent every time the Agent completes a step as it works on a task.

```json
{ 
    "event": "agent_step_completed",
    "data": {
        "step": {

        }
    }
}
```


**Agent Completed**

This event is sent when the Agent completes working on a task.

```json
{ "event": "agent_completed" }
```