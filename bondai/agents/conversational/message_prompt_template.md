{%- if message.type == 'TOOL' %}
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
{% if message.success }
# Tool Response:
```
{{ message.response }}
```
{%- else %}
# Tool Error:
This tool did not run successfully and returned the following error:
```
{{ str(message.error) }}
```
{% endif %}
{%- else %}
{{ message.sender_name.lower() }} to {{ message.recipient_name.lower() }}: {{ message.message }}
{%- endif %}