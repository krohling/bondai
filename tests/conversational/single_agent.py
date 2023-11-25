from bondai.models.openai import get_total_cost, OpenAILLM, OpenAIModelNames
from bondai.tools.file import FileWriteTool
from bondai.agents.conversational import ConversationalAgent

agent_a1 = ConversationalAgent(
    name='Sydney', 
    persona="You are a helpful AI agent. Your goal is to help the user with their task.",
    tools=[FileWriteTool()],
)

message = "Start the conversation by sending the first message. You can exit any time by typing 'exit'."
while True:
    user_input = input(message+ '\n')
    response = agent_a1.send_message(user_input)
    if response:
        message = response.message
        if message.lower() == 'exit':
            break
    else:
        print("The agent has exited the conversation.")
        break
