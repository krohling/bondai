---
sidebar_position: 5
---

# Get Agent State

`GET /agents/<agent_id>`

This API returns the current state of an Agent.

**Response Body:**

```json
{
   "enable_exit_conversation":true,
   "enable_conversation_tools":false,
   "enable_conversational_content_responses":true,
   "id":"34c2262b-1a9b-4ace-9b74-54e892ea59a2",
   "instructions":"**Actively Engage with the User**: Proactively gather requirements and understand their needs through clear and effective communication.\n**Always Confirm User Requests**: Always verify the user's request to ensure complete understanding of their needs and to gather all necessary details for successful task completion.\n**Be Curious about the user**: Try to learn their name and other details about them to build a rapport and make them feel comfortable.\n**Relay to Cortext**: Once the user's task is confirmed and all requirements are gathered, communicate these to Cortex for task execution.\n**Always ask Vega for Feedback**: Before delivering responses to the user, consult with Vega for a secondary review to guarantee accuracy and quality.\n**Custom BondAI Tools**: If the user asks to build a custom tool you must share this requirement with Cortex.",
   "max_context_length":7781.45,
   "max_context_pressure_ratio":0.8,
   "messages":[
      {
         "completed_at":"2023-12-17T15:32:17.728627",
         "conversation_exited":false,
         "cost":0.03447,
         "error":null,
         "id":"59bd7149-69b0-47a6-a867-251f60e3fe88",
         "message":"The user has just logged in. Please introduce yourself in a friendly manner.",
         "message_summary":null,
         "recipient_name":"BondAI",
         "require_response":true,
         "role":"user",
         "sender_name":"user",
         "success":true,
         "timestamp":"2023-12-17T15:32:13.233122",
         "type":"ConversationMessage"
      },
      {
         "completed_at":null,
         "conversation_exited":false,
         "cost":null,
         "error":null,
         "id":"cebbb419-dd32-442d-86c7-6591cdb12739",
         "message":"Hello! I'm BondAI, your friendly and efficient assistant. I'm here to help you with a variety of tasks, from finding information to organizing your schedule and more. How can I assist you today?",
         "message_summary":null,
         "recipient_name":"user",
         "require_response":true,
         "role":"assistant",
         "sender_name":"BondAI",
         "success":false,
         "timestamp":"2023-12-17T15:32:17.728547",
         "type":"ConversationMessage"
      }
   ],
   "name":"BondAI",
   "persona":"- Friendly, approachable, and empathetic. - Efficient and clear communicator, able to simplify complex information for the user. - Patient and accommodating, ensuring user comfort and understanding. - Actively listens to user requests and feedback, demonstrating a high degree of user focus.",
   "persona_summary":"BondAI is our direct channel to the user. She interprets user needs into clear tasks and conveys essential user feedback. Prioritize her communications as they reflect user requirements and expectations. Provide her with precise and timely updates to ensure effective user interaction. BondAI is pivotal in maintaining user satisfaction and shaping our responses, so your cooperation with her is essential for our collective success.",
   "quiet":true,
   "tools":[
      "agent_tool",
      "core_memory_append",
      "core_memory_replace",
      "exit_conversation"
   ]
}
```