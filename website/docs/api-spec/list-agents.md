---
sidebar_position: 2
---

# List Agents

`GET /agents`

This API returns a list of all active Agents.

**Response Body:**

```json
[
    {
        "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc",
        "state":"AGENT_STATE_STOPPED",
        "previous_messages":[ ... ],
        "previous_steps":[ ... ],
        "tools":[ ... ]
    }
]
```