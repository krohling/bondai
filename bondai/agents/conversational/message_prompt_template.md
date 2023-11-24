{%- if message.role == 'tool' %}
# Tool Name
You used the **{{ message.tool_name }}** tool.
{% if message.tool_arguments %}
# Tool Arguments
{% for k, v in message.tool_arguments.items() %}
{{ k }}:
```
{{ v }}
```
{% endfor %}
{% endif %}
{% if message.error %}
# Tool Error:
This tool did not run successfully and returned the following error:
```
{{ str(message.error) }}
```
{%- else %}
# Tool Response:
```
{{ message.response }}
```
{% endif %}
{%- elif message.role == 'status' %}
{{ message.message }}
{%- elif message.role == 'user' or message.role == 'agent' %}
{% if message.error %}
This message failed with the following error:
```
{{ message.error }}
```
Message content:
```
{{ message.sender_name.lower() }} to {{ message.recipient_name.lower() }}: {{ message.message }}
```
{%- else %}
{{ message.sender_name.lower() }} to {{ message.recipient_name.lower() }}: {{ message.message }}
{%- endif %}
{%- endif %}