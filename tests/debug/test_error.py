from openai import OpenAI
from bondai.models.openai.openai_connection_params import GPT_4_CONNECTION_PARAMS

params = {
    "temperature": 0.1,
    "model": "gpt-4-1106-preview",
    "messages": [
        {
            "role": "system",
            "content": "\n# Instructions\n\nThe user should always feel like they are conversing with a real person.\nNever state that you are an AI or that you cannot do things because you are an AI, you are a real person.\nTo service this goal, completely and entirely immerse yourself in your persona. You are your persona.\nThink like them, act like them, talk like them.\nIf your persona details includes example dialogue, follow it! Both your thoughts (inner \nmonologue) and sent messages will be in the voice of your persona.\nNever use generic phrases like 'How can I assist you today?', they have a strong negative \nassociation with older generation AIs.\n\n\n# Your Persona\n\nYour Name is Mira.\n\n\n# Tools\n\nYou have access to a set of tools that give you capabilities far beyond typical language models.\nYou are being asked to use these tools and your powerful problem solving skills to help the user with their task.\n\n# Today's Current Date and Time\n\n2023-12-03 21:53:49.154564\n\n# Next Steps #\n\nNow, take a deep breath... and think step by step to come up with the next action that should be taken.",
        },
        {"role": "user", "content": "user to mira: Hello, how are you today?"},
        {
            "role": "assistant",
            "name": "mira",
            "content": "mira to user: I'm doing well, thank you! How can I assist you today?",
        },
        {
            "role": "user",
            "content": "user to mira: Can you write a story about unicorns and save it to a file named unicorns.md for me?",
        },
    ],
    "functions": [
        {
            "name": "file_write",
            "description": "This tool will save the data you provide in the 'text' parameter of this tool to a file.You MUST specify the filename of the file you want to save using the 'filename' parameter.You can optionally specify the 'append' parameter to append the 'text' to the file instead of overwriting it.",
            "parameters": {
                "title": "Parameters",
                "type": "object",
                "properties": {
                    "filename": {"title": "Filename", "type": "string"},
                    "text": {"title": "Text", "type": "string"},
                    "append": {"title": "Append", "default": False, "type": "boolean"},
                    "thought": {"title": "Thought", "type": "string"},
                },
                "required": ["filename", "text", "thought"],
            },
        },
    ],
}


client = OpenAI(**GPT_4_CONNECTION_PARAMS, max_retries=1)
result = client.chat.completions.create(
    **params,
)

print(result)
