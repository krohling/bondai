---
sidebar_position: 4
---

# Add Agent Tool

`POST /agent/tools`

This API adds a tool to the Agent so it can be used for future tasks. To see a list of available tools check [Get Tools](./get-tools).

**Request Body:**

```json
{
    "tool_name": "file_query_tool"
}
```
