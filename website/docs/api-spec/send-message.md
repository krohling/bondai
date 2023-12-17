---
sidebar_position: 3
---

# Send Message

`POST /agents/<agent_id>/messages`

This API will send a message to an agent.

**Request Schema:**

```json
{
    "message": "I want you to write a story about unicorns."
}
```

**Response Schema:**

```json
{
    "status": "success"
}
```