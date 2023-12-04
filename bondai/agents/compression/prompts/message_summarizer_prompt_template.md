Read the following conversation and summarize the final message:

# Conversation
{% for msg in previous_messages %}
- {{ msg }}
{% endfor %}
- {{ message }}

# Important Rules
- Use the preceding conversation as context but summarize ONLY the following message.
- Your summary must be no longer than {max_words} words.
- Output only the summary. Do NOT include anything else in your output.

Message To Summarize:
{{ message }}

Summary: