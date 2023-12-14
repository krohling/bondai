import os
from typing import Callable
from bondai.prompt import JinjaPromptBuilder
from bondai.util import load_local_resource
from .archival.datasources import (
    ArchivalMemoryDataSource,
    InMemoryArchivalMemoryDataSource,
    PersistentArchivalMemoryDataSource,
)
from .archival.tools import ArchivalMemoryInsertTool, ArchivalMemorySearchTool
from .conversation.datasources import (
    ConversationMemoryDataSource,
    InMemoryConversationMemoryDataSource,
    PersistentConversationMemoryDataSource,
)
from .conversation.tools import (
    ConversationMemorySearchTool,
    ConversationMemorySearchDateTool,
)
from .core.datasources import (
    CoreMemoryDataSource,
    InMemoryCoreMemoryDataSource,
    PersistentCoreMemoryDataSource,
)
from .core.tools import CoreMemoryAppendTool, CoreMemoryReplaceTool

DEFAULT_PROMPT_TEMPLATE = load_local_resource(
    __file__, os.path.join("prompts", "default_prompt_template.md")
)


class MemoryManager:
    def __init__(
        self,
        core_memory_datasource: CoreMemoryDataSource | None = None,
        conversation_memory_datasource: ConversationMemoryDataSource | None = None,
        archival_memory_datasource: ArchivalMemoryDataSource | None = None,
        prompt_builder: Callable[..., str] = JinjaPromptBuilder(
            DEFAULT_PROMPT_TEMPLATE
        ),
    ):
        self._core_memory_datasource = core_memory_datasource
        self._conversation_memory_datasource = conversation_memory_datasource
        self._archival_memory_datasource = archival_memory_datasource
        self._prompt_builder = prompt_builder

    @property
    def core_memory(self) -> CoreMemoryDataSource:
        return self._core_memory_datasource

    @property
    def conversation_memory(self) -> ConversationMemoryDataSource:
        return self._conversation_memory_datasource

    @property
    def archival_memory(self) -> ArchivalMemoryDataSource:
        return self._archival_memory_datasource

    @property
    def tools(self):
        tools = []
        if self._core_memory_datasource:
            tools.extend(
                [
                    CoreMemoryAppendTool(self._core_memory_datasource),
                    CoreMemoryReplaceTool(self._core_memory_datasource),
                ]
            )
        if self._conversation_memory_datasource:
            tools.extend(
                [
                    ConversationMemorySearchTool(self._conversation_memory_datasource),
                    ConversationMemorySearchDateTool(
                        self._conversation_memory_datasource
                    ),
                ]
            )
        if self._archival_memory_datasource:
            tools.extend(
                [
                    ArchivalMemoryInsertTool(self._archival_memory_datasource),
                    ArchivalMemorySearchTool(self._archival_memory_datasource),
                ]
            )
        return tools

    def __call__(self):
        return self.render_prompt_section()

    def render_prompt_section(self) -> str:
        return self._prompt_builder(
            core_memory_datasource=self._core_memory_datasource,
            conversation_memory_datasource=self._conversation_memory_datasource,
            archival_memory_datasource=self._archival_memory_datasource,
        )


class PersistentMemoryManager(MemoryManager):
    def __init__(
        self,
        prompt_builder: Callable[..., str] | None = None,
    ):
        if prompt_builder is None:
            prompt_builder = JinjaPromptBuilder(DEFAULT_PROMPT_TEMPLATE)
        super().__init__(
            core_memory_datasource=PersistentCoreMemoryDataSource(),
            conversation_memory_datasource=PersistentConversationMemoryDataSource(),
            archival_memory_datasource=PersistentArchivalMemoryDataSource(),
            prompt_builder=prompt_builder,
        )


class ConversationalMemoryManager(MemoryManager):
    def __init__(
        self,
        conversation_memory_datasource: ConversationMemoryDataSource | None = None,
        prompt_builder: Callable[..., str] | None = None,
    ):
        if conversation_memory_datasource is None:
            conversation_memory_datasource = InMemoryConversationMemoryDataSource()
        if prompt_builder is None:
            prompt_builder = JinjaPromptBuilder(DEFAULT_PROMPT_TEMPLATE)
        super().__init__(
            core_memory_datasource=None,
            conversation_memory_datasource=conversation_memory_datasource,
            archival_memory_datasource=None,
            prompt_builder=prompt_builder,
        )
