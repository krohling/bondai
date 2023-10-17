---
sidebar_position: 4
---

# Add Agent Tool

`POST /agent/<agent_id>/tools`

This API adds a tool to an Agent so it can be used for future tasks. 

**Request Body:**

```json
{
    "tool_name": "file_query_tool"
}
```
