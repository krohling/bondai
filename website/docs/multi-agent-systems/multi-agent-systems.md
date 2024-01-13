---
sidebar_position: 4
---

# Multi-Agent Systems

Multi-Agent Systems (MAS) in BondAI represent a sophisticated approach to developing interactive, collaborative AI applications. At the core of MAS in BondAI are three primary classes: [ConversationalAgent](../agents/conversational-agent.md), [GroupConversation](./group-conversation.md), and [TeamConversationConfig](./team-conversation-config.md).

**ConversationalAgent** acts as the fundamental building block of MAS, embodying individual agents with specific roles or expertise. These agents can engage in dialogues, process information, and perform tasks based on their programming and interactions.

**GroupConversation** is the framework that orchestrates communication among multiple agents. It allows various ConversationalAgents to interact within a shared conversational space, enabling information exchange, collaborative problem-solving, and decision-making processes. This class manages the dynamics of the conversation, ensuring coherent interactions among all participating agents.

**TeamConversationConfig** is crucial for structuring the conversation architecture within a MAS. It defines how agents are grouped and how they can communicate with each other. This configuration can set up hierarchical structures, dividing agents into teams or layers, and determining the flow of information between them. It plays a pivotal role in managing complex conversations where different agents contribute distinct insights or skills towards a common goal.

Together, these classes enable the development of complex MAS architectures in BondAI, where agents can work in unison or independently, mimicking real-world team dynamics and collaborative environments. This system opens up possibilities for applications requiring nuanced interactions and emergent intelligence.