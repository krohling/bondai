---
sidebar_position: 3
---


# TeamConversationConfig

The TeamConversationConfig class in BondAI structures the conversations in a Multi-Agent System, enabling complex conversational patterns among different agents.


```python
class TeamConversationConfig(BaseGroupConversationConfig):
    def __init__(self, *args: List[ConversationMember]):
        ...
```

## Usage Example

```python
from bondai.agents import ConversationalAgent
from bondai.agents.group_chat import GroupConversation, TeamConversationConfig

# Initialize team 1
agent1 = ConversationalAgent(...)
agent2 = ConversationalAgent(...)
team1 = [agent1, agent2]

# Initialize team 2
agent3 = ConversationalAgent(...)
agent4 = ConversationalAgent(...)
team2 = [agent3, agent4]

# Allow agent1 and agent 3 to communicate
team3 = [agent1, agent3]

# Configure teams
team_config = TeamConversationConfig(team1, team2, team3)

# Use in GroupConversation
group_conversation = GroupConversation(conversation_config=team_config)
```


## Key Features

- Facilitates hierarchical and structured team-based conversations.
- Allows the creation of any number of teams with specific member agents.
- Supports dynamic interactions within and across teams.
- Enhances the control over communication flow in multi-agent setups.
