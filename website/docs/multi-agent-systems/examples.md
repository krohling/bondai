---
sidebar_position: 1
---

# Multi-Agent Architectures

## Example 1: Flat Multi-Agent Architecture

In this example architecture, multiple ConversationalAgents are configured, each specializing in different aspects of customer support (e.g., technical, billing, general queries). They are managed under a GroupConversation system. This is an example of a flat conversational architecture where all agents are able to communicate directly with each other.

```python
from bondai.agents import ConversationalAgent
from bondai.agents.group_chat import GroupConversation

# Initialize multiple agents for different support aspects
tech_support = ConversationalAgent(name="TechSupport")
billing_support = ConversationalAgent(name="BillingSupport")
general_support = ConversationalAgent(name="GeneralSupport")

# Create a group conversation with these agents
support_team = GroupConversation(
    conversation_members=[
        tech_support, 
        billing_support, 
        general_support
    ]
)

# Code to route user queries to the appropriate agent
user_query = "How do I reset my password?"
response = support_team.send_message(tech_support.name, user_query)
print(response.message)
```

## Example 2: Hierarchical Conversational Architecture

This example illustrates a hierarchical conversational architecture, characterized by structured agent interactions within a group. In this setup, the GroupConversation is configured using TeamConversationConfig to create distinct teams within the conversation.

- **Agent Configuration**: Three ConversationalAgent's are initialized—`team_leader`, `coding_expert`, and `design_expert`. Each agent has a specific role, where the team leader can coordinate and delegate tasks between the two experts.

- **Group Setup**: The GroupConversation is organized into teams: one team includes the `team_leader` and `coding_expert`, and another consists of the `team_leader` and `design_expert`. This configuration ensures that the team leader can communicate with both experts, but direct communication between the coding and design experts is not possible.

- **Conversation Dynamics**: When the conversation starts, a message is sent to the `team_leader`. The hierarchical structure allows the team leader to relay information to the experts, orchestrate their collaboration, and provide combined insights from both agents.

```python
from bondai.agents import ConversationalAgent
from bondai.agents.group_chat import GroupConversation, TeamConversationConfig

# Initialize team agents
team_leader = ConversationalAgent(name="TeamLeader")
coding_expert = ConversationalAgent(name="CodingExpert")
design_expert = ConversationalAgent(name="DesignExpert")

# Create a group conversation
problem_solving_team = GroupConversation(
    conversation_config=TeamConversationConfig(
        [team_leader, coding_expert],
        [team_leader, design_expert]
    )
)

# Simulate a problem-solving session
problem_description = "Develop a user-friendly app interface."
response = problem_solving_team.send_message(team_leader.name, problem_description)
print(response.message)
```


## Example 3: Multi-Team, Heirarchical Conversational Architecture

This example showcases a complex hierarchical architecture, involving multiple agents organized into distinct teams, each with specialized roles. In this model, communication channels are both vertical (within each team) and horizontal (across teams via team leaders).

- **Agent Configuration**: The architecture involves a `product_manager`, two team leaders (`eng_leader` and `design_leader`), and various experts (`coding_expert`, `qa_expert`, `visual_designer`, `ux_designer`). The `product_manager` serves as a central figure overseeing the entire project.

- **Group Setup**: This configuration organizes the agents into three teams: an **engineering team** (led by `eng_leader`), a **design team** (led by `design_leader`), and a **management team** consisting of the `product_manager` and both team leaders.

- **Conversation Dynamics**: When a conversation is initiated, a message is sent to the `product_manager`, the product manager can facilitate the conversation by engaging with both team leaders, who in turn can collaborate with their respective team members.


```python
from bondai.agents import ConversationalAgent
from bondai.agents.group_chat import GroupConversation, TeamConversationConfig

# Initialize product manager agent
product_manager = ConversationalAgent(name="ProductManager")

# Initialize team 1 agents
eng_leader = ConversationalAgent(name="EngTeamLeader")
coding_expert = ConversationalAgent(name="CodingExpert")
qa_expert = ConversationalAgent(name="QAExpert")

# Initialize team 2 agents
design_leader = ConversationalAgent(name="DesignTeamLeader")
visual_designer = ConversationalAgent(name="VisualDesigner")
ux_designer = ConversationalAgent(name="UXDesigner")

# Create a group conversation
problem_solving_team = GroupConversation(
    conversation_config=TeamConversationConfig(
        [eng_leader, coding_expert, qa_expert],
        [design_leader, visual_designer, ux_designer],
        [product_manager, eng_leader, design_leader]
    )
)

# Simulate a problem-solving session
problem_description = "Develop a user-friendly app interface."
response = problem_solving_team.send_message(product_manager.name, problem_description)
print(response.message)
```