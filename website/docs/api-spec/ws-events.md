---
sidebar_position: 6
---

# WebSocket Events

The BondAI API server will host a WebSocket endpoint on the specified server port (default: 2663). The following events are supported.

## Conversational Agent Events

**Conversational Agent Started**

This event is sent when the Conversational Agent first starts. This usually occurs after the [Start Agent](./start-agent) API Endpoint is called.

```json
{
    "event": "conversational_agent_started",
    "data": {
        "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc",
    }
}
```

**Conversational Agent Completed**

This event is sent when the Conversational Agent is stops. This usually occurs after the [Stop Agent](./stop-agent) API Endpoint is called.

```json
{
    "event": "conversational_agent_completed",
    "data": {
        "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc",
    }
}
```

**Conversational Agent Message**

This event is sent when the Conversational Agent wants to communicate with the user.

```json
{
    "event": "conversational_agent_message",
    "data": {
        "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc",
        "message": "How can I help you today?"
    }
}
```

## User Events

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

## Task Agent Events

**Task Agent Started**

This event is sent when the Task Agent begins working on a task. This usually occurs once the Conversational Agent has finished gathered information from the user about what task needs to be completed.

```json
{
    "event": "task_agent_started",
    "data": {
        "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc"
    }
}
```

**Task Agent Completed**

This event is sent when the Task Agent finishes working on a task.

```json
{
    "event": "task_agent_completed",
    "data": {
        "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc"
    }
}
```

**Step Started**

This event is sent every time the Task Agent starts a new step as it works on a task.

```json
{
    "event": "task_agent_step_started",
    "data": {
        "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc"
    }
}
```

**Step Tool Selected**

This event is sent every time the Task Agent selects a tool for each step as it works on a task.

```json
{
    "event": "task_agent_step_tool_selected",
    "data": {
        "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc",
        "step": { ... }
    }
}
```

**Step Completed**

This event is sent every time the Task Agent completes a step as it works on a task.

```json
{ 
    "event": "task_agent_step_completed",
    "data": {
        "step": {
            "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc",
            "step": { ... }
        }
    }
}
```
