from bondai.api import BondAIAPIClient

task = "I want you to write a story about unicorns and save it to a file named unicorns.md."

# Create the client
client = BondAIAPIClient()

# Connect to the WebSocket
client.connect_ws()

@client.on("conversational_agent_started")
def handle_conversational_agent_started(agent_id):
    print('Conversational Agent started.')

@client.on("conversational_agent_message")
def handle_conversational_agent_message(agent_id, message):
    print(message)
    print("Enter your response:")
    user_message=input()
    client.send_user_message(agent_id, user_message)

@client.on("conversational_agent_completed")
def handle_conversational_agent_completed(agent_id):
    print("Conversational Agent completed.")

@client.on("task_agent_started")
def handle_task_agent_started(agent_id):
    print('Task Agent started.')

@client.on("task_agent_completed")
def handle_task_agent_completed(agent_id):
    print("Task Agent completed.")

@client.on("task_agent_step_started")
def handle_task_agent_step_started(agent_id):
    print("Task Agent step started.")

@client.on("task_agent_step_tool_selected")
def handle_task_agent_step_tool_selected(agent_id, message):
    print("Task Agent step tool selected.")
    print(message)

@client.on("task_agent_step_completed")
def handle_task_agent_step_completed(agent_id, message):
    print("Task Agent step completed.")
    print(message)


# Create the Agent
response = client.create_agent()
agent_id = response['agent_id']
# print("*****Create Agent*****")
# print(response)

# print("*****List Agents*****")
# print(client.list_agents())

# print("*****Get Agent*****")
# print(client.get_agent(agent_id))

# print("*****Get Agent Tool Options*****")
# print(client.get_agent_tool_options(agent_id))

# print("*****Get Agent Tools*****")
# print(client.get_agent_tools(agent_id))

# print("*****Remove Agent Tool*****")
# print(client.remove_agent_tool(agent_id, 'download_file'))

# print("*****Add Agent Tool*****")
# print(client.add_agent_tool(agent_id, 'download_file'))

# print("*****Get Settings*****")
# print(client.get_settings())

# print("*****Set Settings*****")
# print(client.set_settings({
#     'tools': [
#         {
#             'key': 'BLAND_AI_API_KEY',
#             'value': '1234'
#         }
#     ]
# }))



# Start the Agent
response = client.start_agent(agent_id)

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")