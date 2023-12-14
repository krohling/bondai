from bondai.models.openai import get_total_cost, OpenAILLM, OpenAIModelNames
from bondai.tools.file import FileWriteTool
from bondai.agents import ConversationalAgent
from bondai.util.caching import PersistentLLMCache

llm = OpenAILLM(OpenAIModelNames.GPT4_TURBO_1106, cache=PersistentLLMCache())
agent = ConversationalAgent(
    llm=llm,
    tools=[FileWriteTool()],
)

message = "Start the conversation by sending the first message. You can exit any time by typing 'exit'."
while True:
    user_input = input(message + "\n")
    if user_input.lower() == "exit":
        break
    response = agent.send_message(user_input)
    if response:
        message = response.message
    else:
        print("The agent has exited the conversation.")
        break

print(f"Total Cost: {get_total_cost()}")
