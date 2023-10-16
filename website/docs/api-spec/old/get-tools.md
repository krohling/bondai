---
sidebar_position: 2
---

# Get Tools

`GET /tools`

This API returns the list of all of tools that BondAI has loaded. These tools can be given to the Agent so that it can use them when working on a task. To see what tools the Agent is using see [Get Agent](./get-agent).

**Response Body:**

```json
[
   {
      "description":"This tool allows to you to download a file. Just provide the url to the file in the 'url' parameter and the filename it should be saved to in the 'filename' parameter.",
      "name":"download_file",
      "parameters":{
         "properties":{
            "filename":{
               "title":"Filename",
               "type":"string"
            },
            "thought":{
               "title":"Thought",
               "type":"string"
            },
            "url":{
               "title":"Url",
               "type":"string"
            }
         },
         "required":[
            "url",
            "filename",
            "thought"
         ],
         "title":"Parameters",
         "type":"object"
      }
   },
   {
      "description":"This tool will save the data you provide in the 'text' parameter of this tool to a file.You MUST specify the filename of the file you want to save using the 'filename' parameter.You can optionally specify the 'append' parameter to append the 'text' to the file instead of overwriting it.",
      "name":"file_write",
      "parameters":{
         "properties":{
            "append":{
               "default":false,
               "title":"Append",
               "type":"boolean"
            },
            "filename":{
               "title":"Filename",
               "type":"string"
            },
            "text":{
               "title":"Text",
               "type":"string"
            },
            "thought":{
               "title":"Thought",
               "type":"string"
            }
         },
         "required":[
            "filename",
            "text",
            "thought"
         ],
         "title":"Parameters",
         "type":"object"
      }
   }
]
```

