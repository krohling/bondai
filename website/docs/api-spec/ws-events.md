---
sidebar_position: 10
---

# WebSocket Events

The BondAI API server will host a WebSocket endpoint on the specified server port (default: 2663). The following events are supported.

**Agent Message**

This event is sent when the Agent wants to communicate with the user.

```json
{
   "event":"agent_message",
   "data":{
      "agent_id":"c66695ce-1ba8-485e-ab85-44583ed4e120",
      "message":{
         "id":"54598660-0a73-455c-b365-69b47118fab0",
         "role":"assistant",
         "timestamp":"2023-12-17T15:13:45.534012",
         "sender_name":"BondAI",
         "recipient_name":"user",
         "message":"Hello! I'm BondAI, your friendly assistant. I'm here to help you with any tasks or information you need. How can I assist you today?",
         "message_summary":null,
         "require_response":true,
         "success":false,
         "error":null,
         "conversation_exited":false,
         "cost":null,
         "completed_at":null,
         "type":"ConversationMessage"
      }
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

**Streaming Content Updates**

This event can be used to stream Agent responses to the end user. This event is fired as new chunks of content are received from the LLM.

```json
{
   "event":"streaming_content_updated",
   "data":{
      "agent_id":"121f6cbb-15e1-4464-8a1b-7e6540098ae5",
      "content_buffer":" Hello"
   }
}
```

**Streaming Function Updates**

This event is fired as new chunks are received from the LLM for use with a specific function.

```json
{
   "event":"streaming_function_updated",
   "data":{
      "agent_id":"121f6cbb-15e1-4464-8a1b-7e6540098ae5",
      "function_name":"agent_tool",
      "arguments_buffer":"{\n  \"task_description\": \"Write a story about unicorns and save it to a file named unicorns.md\"\n"
   }
}
```

**Tool Selected**

This message indicates that the Agent has selected a tool. The `data` property will include the parameters being used to execute the tool.

```json
{
   "event":"tool_selected",
   "data":{
      "agent_id":"121f6cbb-15e1-4464-8a1b-7e6540098ae5",
      "message":{
         "id":"7f173c50-c011-4d7f-949d-5ed08ed1d372",
         "role":"function",
         "timestamp":"2023-12-17T15:24:35.503669",
         "tool_name":"file_write",
         "tool_arguments":{
            "filename":"unicorns.md",
            "text":"# The Enchanted Forest of Unicorns\n\nOnce upon a time...",
            "thought":"Writing a story about unicorns and saving it to a file named unicorns.md"
         },
         "tool_output":null,
         "tool_output_summary":null,
         "success":false,
         "error":null,
         "agent_halted":false,
         "cost":null,
         "completed_at":null,
         "type":"ToolUsageMessage"
      }
   }
}
```

**Tool Completed**

This message indicates that the Agent has successfully completed running a tool. The `data` property will include the output received from the tool.

```json
{
   "event":"tool_completed",
   "data":{
      "agent_id":"121f6cbb-15e1-4464-8a1b-7e6540098ae5",
      "message":{
         "id":"7f173c50-c011-4d7f-949d-5ed08ed1d372",
         "role":"function",
         "timestamp":"2023-12-17T15:24:35.503669",
         "tool_name":"file_write",
         "tool_arguments":{
            "filename":"unicorns.md",
            "text":"# The Enchanted Forest of Unicorns\n\nOnce upon a time...",
            "thought":"Writing a story about unicorns and saving it to a file named unicorns.md"
         },
         "tool_output":"File unicorns.md written successfully",
         "tool_output_summary":null,
         "success":true,
         "error":null,
         "agent_halted":false,
         "cost":0.0,
         "completed_at":"2023-12-17T15:24:35.505959",
         "type":"ToolUsageMessage"
      }
   }
}
```

**Tool Error**

This message indicates that the Agent has encountered an error when running a tool. The `data` property will include the error message.

```json
{
   "event":"tool_error",
   "data":{
      "agent_id":"121f6cbb-15e1-4464-8a1b-7e6540098ae5",
      "message":{
         "id":"4624c923-4712-4a9b-8323-b600c41469c5",
         "role":"function",
         "timestamp":"2023-12-17T15:24:54.036341",
         "tool_name":"file_query",
         "tool_arguments":{
            "filename":"unicorns.md",
            "question":"What is the content of the file?",
            "thought":"I need to read the content of the file to review the story about unicorns."
         },
         "tool_output":null,
         "tool_output_summary":null,
         "success":false,
         "error":"The following error occurred...",
         "agent_halted":false,
         "cost":0.0,
         "completed_at":"2023-12-17T15:24:54.324382",
         "type":"ToolUsageMessage"
      }
   }
}
```

