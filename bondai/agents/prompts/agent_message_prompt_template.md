{%- if message_type == "ToolUsageMessage" %}
# Message Timestamp
{{ message.timestamp }}

# Tool Name
You used the **{{ message.tool_name }}** tool.
# Tool Arguments
{% if message.tool_arguments %}
{% for k, v in message.tool_arguments.items() %}
{{ k }}:
```
{{ v }}
```
{% endfor %}
{%- else %}
No arguments were provided for this tool.
{% endif %}
{% if message.error %}
# Tool Error:
This tool did not run successfully and returned the following error:
```
{{ message.error }}
```
{%- else %}
# Tool Response:
```
{{ message.tool_output_summary or message.tool_output }}
```
{% endif %}
{%- elif message_type == "SystemMessage" %}
# Message Timestamp
{{ message.timestamp }}

{{ message.message }}
{%- elif message_type == "SummaryMessage" %}
The following is a summary of the previous conversation content. It has been summarized to save memory space:
{{ message.message }}
{%- elif message_type == "ConversationMessage" %}
{% if message.error %}
This message failed with the following error:
```
{{ message.error }}
```
Message content:
```
{{ message.sender_name.lower() }} to {{ message.recipient_name.lower() }}: {{ message.message_summary or message.message }}
```
{%- else %}
{{ message.sender_name.lower() }} to {{ message.recipient_name.lower() }}: {{ message.message_summary or message.message }}
{%- endif %}
{%- endif %}