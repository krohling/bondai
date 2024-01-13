---
sidebar_position: 5
---

# Memory Management

Memory Management in BondAI is inspired by the tiered memory approach detailed in the [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/pdf/2310.08560.pdf) paper. This system mirrors operating systems' memory hierarchies, enhancing large language models' (LLMs) ability to handle extensive contexts and complex conversations. The memory system in BondAI consists of:

- **Core Memory**: Directly integrated into the agent's system prompt, this memory system provides immediate access to essential, current information relevant to ongoing tasks but is limited in size.

- **Conversation Memory**: Captures the complete history of conversational interactions, allowing agents to use keyword search to reference past dialogues.

- **Archival Memory**: Effectively limitless in size, it stores extensive historical data and information. Using semantic search, enabled by the `faiss` library, Archival Memory allows agents to easily access extremely large datasets via what is effectively an implicit RAG pipeline.

All of these memory systems are automatically managed by the **MemoryManager** class which automatically equips BondAI agents with the necessay tools for searching and editing their memory systems. Additionally, the **MemoryManager** is responsible for updating the Agent's system prompt to ensure the appopriate information is included.
