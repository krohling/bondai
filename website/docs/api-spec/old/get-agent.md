---
sidebar_position: 3
---

# Get Agent

`GET /agent`

This API returns the current state of the Agent including all messages, the steps it has taken toward it's current task and the tools it has access to for it's current task.

**Response Body:**

```json
{
   "state":"AGENT_STATE_STOPPED",
   "previous_messages":[
      
   ],
   "previous_steps":[
      
   ],
   "tools":[
      {
         "description":"This tool allows you to ask a question about the text content of any file including summarization. This tool works for text files, html files and PDFs. Just specify the filename of the file using the 'filename' parameter and specify your question using the 'question' parameter.",
         "name":"file_query",
         "parameters":{
            "properties":{
               "filename":{
                  "title":"Filename",
                  "type":"string"
               },
               "question":{
                  "title":"Question",
                  "type":"string"
               },
               "thought":{
                  "title":"Thought",
                  "type":"string"
               }
            },
            "required":[
               "filename",
               "question",
               "thought"
            ],
            "title":"Parameters",
            "type":"object"
         }
      },
   ]
}
```