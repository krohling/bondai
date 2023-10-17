---
sidebar_position: 6
---

# Start Agent

`POST /agent/start`

This API will start the Agent's execution against the specified task.

**Request Body:**

```json
{
    "task": "A detailed description of the task you would like the Agent to complete.",
    "task_budget": 10.0,
    "max_steps": 10
}
```

**Parameters**

- **task** (optional) - This is a description of the task you would like the Agent to work on.
- **task_budget** (optional) - This is the maximum budget for OpenAI API calls that you would like to use for this task.
- **max_steps** (optional) - This is the maximum number of steps that you would like the Agent to take to complete this task.
