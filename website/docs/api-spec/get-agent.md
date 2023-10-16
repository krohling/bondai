---
sidebar_position: 3
---

# Get Agent

`GET /agents/<agent_id>`

This API returns a an Agent by ID.

**Response Body:**

```json
{
    "agent_id": "43895600-d333-4d45-97a8-e9c4400405cc",
    "state":"AGENT_STATE_STOPPED",
    "previous_messages":[ ... ],
    "previous_steps":[ ... ],
    "tools":[ ... ]
}
```