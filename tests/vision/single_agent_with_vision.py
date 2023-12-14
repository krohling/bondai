from datetime import datetime
from bondai.models.openai import get_total_cost
from bondai.tools.vision import ImageAnalysisTool
from bondai.agents import ConversationalAgent

agent = ConversationalAgent(tools=[ImageAnalysisTool()])

message = "Start the conversation by sending the first message. You can exit any time by typing 'exit'."
while True:
    user_input = input(message + "\n")
    if user_input.lower() == "exit":
        break
    response = agent.send_message(user_input)
    response.success = True
    response.completed_at = datetime.now()

    if response:
        message = response.message
        if message.lower() == "exit":
            break
    else:
        print("The agent has exited the conversation.")
        break

print(f"Total Cost: {get_total_cost()}")
