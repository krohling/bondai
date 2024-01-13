---
sidebar_position: 4
---

# MemoryManager

The MemoryManager class in BondAI is designed to orchestrate the memory management strategy across different types of memory data sources. It used to manage the memory requirements of BondAI agents, including ConversationalAgent and ReAct Agents.

```python
class MemoryManager:
    def __init__(
        self,
        core_memory_datasource: CoreMemoryDataSource | None = None,
        conversation_memory_datasource: ConversationMemoryDataSource | None = None,
        archival_memory_datasource: ArchivalMemoryDataSource | None = None,
        prompt_builder: Callable[..., str] | None = None,
    ):

```

# Usage Example

```python
from bondai.agents import ConversationalAgent
from bondai.memory import MemoryManager, PersistentCoreMemoryDataSource, PersistentConversationMemoryDataSource, PersistentArchivalMemoryDataSource

# Initialize the memory manager with persistent datasources
memory_manager = MemoryManager(
    core_memory_datasource=PersistentCoreMemoryDataSource(),
    conversation_memory_datasource=PersistentConversationMemoryDataSource(),
    archival_memory_datasource=PersistentArchivalMemoryDataSource()
)

# Configure an Agent to use this MemoryManager
agent = ConversationalAgent(memory_manager=memory_manager)
```

# Key Features

- Manages different types of memory: core, conversation, and archival.
- Provides a unified interface for memory operations across different memory types.
- Automatically manages Agent access to memory systems via LLM tools.
- Updates the Agent system prompt to ensure it's always updated with the latest information.

# Parameters

- **core_memory_datasource**: Instance of CoreMemoryDataSource for core memory operations.
- **conversation_memory_datasource**: Instance of ConversationMemoryDataSource for managing conversation memory.
- **archival_memory_datasource**: Instance of ArchivalMemoryDataSource for long-term memory storage and retrieval.
- **prompt_builder**: Callable for customizing memory-related prompt sections. These are dynamically inserted into the Agent system prompt at runtime.
