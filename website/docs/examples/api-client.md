---
sidebar_position: 4
---

# API Client

This example demonstrates how to use the BondAIAPIClient to communicate with the [BondAI API](../api-spec/getting-started).

```python
from bondai import AGENT_STATE_STOPPED
from bondai.api import BondAIAPIClient

base_url = 'http://127.0.0.1:5000'
client = BondAIAPIClient(base_url=base_url)

@client.on('agent_started')
def handle_agent_started():
    print('Task started')

@client.on('agent_completed')
def handle_agent_completed():
    print('Task completed')

@client.on('agent_message')
def handle_agent_message(message):
    print(message)
    user_message = input("Enter your response: ")
    client.send_user_message(user_message)

@client.on('agent_step_completed')
def handle_agent_step_completed(step):
    print(f"Agent completed step")
    print(step)

client.connect_ws()
agent_state = client.get_agent()
if agent_state['state'] == AGENT_STATE_STOPPED:
    client.start_agent()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")
```