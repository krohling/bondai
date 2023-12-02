from bondai.tools.file import FileWriteTool
from bondai.agents import Agent
from bondai.memory import MemoryManager, PersistantMemoryManager
from util import extract_text_from_directory

memory_manager = PersistantMemoryManager()
memory_manager.core_memory.set('user', 'Name is George. Lives in New York. Has a dog named Max.')
if memory_manager.archival_memory.size == 0:
    memory_manager.archival_memory.insert_bulk(
        extract_text_from_directory('./tests/memory/documents')
    )

agent = Agent(
    tools=[FileWriteTool()] + memory_manager.tools,
    system_prompt_sections=[memory_manager]
)

message = "Start the conversation by sending the first message. You can exit any time by typing 'exit'."
while True:
    user_input = input(message+ '\n')
    if user_input.lower() == 'exit':
        break
    response = agent.send_message(user_input)
    if response:
        message = response.message
        if message.lower() == 'exit':
            break
    else:
        print("The agent has exited the conversation.")
        break
