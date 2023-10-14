from bondai.api import BondAIAPIClient

task = "I want you to write a story about unicorns and save it to a file named unicorns.md."

# Create the client
client = BondAIAPIClient()

# Connect to the WebSocket
client.connect_ws()

# Listen to WebSocket events
@client.on("agent_message")
def handle_agent_message(message):
    print(message)
    print("Enter your response:")
    response=input()
    client.send_user_message(response)

@client.on("agent_started")
def handle_agent_started():
    print('Agent has started.')

@client.on("agent_step_started")
def handle_agent_step_started():
    print("Agent step started.")

@client.on("agent_step_tool_selected")
def handle_agent_step_started(message):
    print("Agent step tool selected.")
    print(message)

@client.on("agent_step_completed")
def handle_agent_step_completed(message):
    print("Agent step completed.")
    print(message)

@client.on("agent_completed")
def handle_agent_completed():
    print('Agent has completed.')

# Start the Agent
response = client.start_agent()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")