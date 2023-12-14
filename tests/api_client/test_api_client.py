from termcolor import cprint
from bondai.api import BondAIAPIClient

# Create the client
client = BondAIAPIClient()
client.connect_ws()
agent = client.create_agent()
user_exited = False


# Listen to WebSocket events
@client.on("streaming_content_updated")
def handle_streaming_content_updated(agent_id, content_buffer):
    if agent_id != agent["id"]:
        return
    print(content_buffer)


@client.on("streaming_function_updated")
def handle_streaming_function_updated(agent_id, function_name, arguments_buffer):
    if agent_id != agent["id"]:
        return
    print(function_name)
    print(arguments_buffer)


@client.on("agent_message")
def handle_agent_message(agent_id, message):
    global user_exited
    if agent_id != agent["id"]:
        return

    cprint("\n" + message["message"] + "\n", "white")
    response = input()
    if response.lower().strip() == "exit":
        client.disconnect_ws()
        user_exited = True
    else:
        client.send_message(agent_id, response)


@client.on("tool_selected")
def handle_tool_selected_message(agent_id, message):
    if agent_id != agent["id"]:
        return

    tool_name = message["tool_name"]
    tool_arguments = message.get("tool_arguments", {})

    if "thought" in tool_arguments:
        cprint(f"Using tool {tool_name}: {tool_arguments['thought']}", "green")
    else:
        cprint(f"Using tool {tool_name}...", "green")


@client.on("tool_error")
def handle_tool_error_message(agent_id, message):
    if agent_id != agent["id"]:
        return

    cprint(message, "red")


cprint("******************ENTERING CHAT******************", "white")
cprint(
    "You are entering a chat with BondAI...\nYou can exit any time by typing 'exit'.",
    "white",
)
intro_message = (
    "The user has just logged in. Please introduce yourself in a friendly manner."
)
client.send_message(agent["id"], intro_message)

try:
    while not user_exited:
        pass
except KeyboardInterrupt:
    print("Exiting...")
