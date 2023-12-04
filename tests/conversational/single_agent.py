from bondai.tools.file import FileWriteTool
from bondai.agents import Agent

agent_a1 = Agent(
    tools=[FileWriteTool()],
)

message = "Start the conversation by sending the first message. You can exit any time by typing 'exit'."
while True:
    user_input = input(message+ '\n')
    if user_input.lower() == 'exit':
        break
    response = agent_a1.send_message(user_input)
    if response:
        message = response.message
    else:
        print("The agent has exited the conversation.")
        break
