from datetime import datetime
from bondai.models.openai import get_total_cost
from bondai.tools.file import FileWriteTool
from bondai.agents import ConversationalAgent
from bondai.memory import MemoryManager
from util import extract_text_from_directory

memory_manager = MemoryManager()
memory_manager.core_memory.set(
    "user", "Name is George. Lives in New York. Has a dog named Max."
)
memory_manager.archival_memory.insert_bulk(
    extract_text_from_directory("./tests/memory/documents")
)

agent = ConversationalAgent(tools=[FileWriteTool()], memory_manager=memory_manager)

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
