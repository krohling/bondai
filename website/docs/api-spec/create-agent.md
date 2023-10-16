---
sidebar_position: 1
---

# Create Agent

`POST /agents/`

This API will create a new Agent but will not start it. To begin communicating with the Agent you must also call the [Start Agent](./start-agent) API endpoint.

**Response Body:**

```json
{
    "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc",
    "state":"AGENT_STATE_STOPPED",
    "previous_messages":[],
    "previous_steps":[],
    "tools":[ ... ]
}
```
