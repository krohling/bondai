from pydantic import BaseModel
from typing import Dict
from bondai.tools import Tool
from .datasources import CoreMemoryDataSource


CORE_MEMORY_APPEND_TOOL_NAME = "core_memory_append"
CORE_MEMORY_APPEND_TOOL_DESCRIPTION = (
    "Use the core_memory_append tool to append to the contents of core memory. "
    "- section: Section of the memory to be edited. \n"
    "- content: Content to write to the memory."
)


class CoreMemoryAppendParameters(BaseModel):
    section: str
    content: str


class CoreMemoryAppendTool(Tool):
    def __init__(self, datasource: CoreMemoryDataSource):
        super().__init__(
            CORE_MEMORY_APPEND_TOOL_NAME,
            CORE_MEMORY_APPEND_TOOL_DESCRIPTION,
            CoreMemoryAppendParameters,
        )
        self._datasource = datasource

    def run(self, section: str, content: str):
        if not section in self._datasource.sections:
            raise ValueError(f"Section {section} does not exist.")

        new_content = self._datasource.get(section) + content
        self._datasource.set(section, new_content)


CORE_MEMORY_REPLACE_TOOL_NAME = "core_memory_replace"
CORE_MEMORY_REPLACE_TOOL_DESCRIPTION = (
    "Use the core_memory_replace tool to replace to the contents of core memory. "
    "To delete memories, use an empty string for new_content. \n"
    "- section: Section of the memory to be edited. \n"
    "- old_content: String to replace. Must be an exact match. \n"
    "- new_content: Content to write to the memory."
)


class CoreMemoryReplaceParameters(BaseModel):
    section: str
    old_content: str
    new_content: str


class CoreMemoryReplaceTool(Tool):
    def __init__(self, datasource: CoreMemoryDataSource):
        super().__init__(
            CORE_MEMORY_REPLACE_TOOL_NAME,
            CORE_MEMORY_REPLACE_TOOL_DESCRIPTION,
            CoreMemoryReplaceParameters,
        )
        self._datasource = datasource

    def run(self, section: str, old_content: str, new_content: str):
        section = section.replace("<", " ").replace(">", " ")
        if not section in self._datasource.sections:
            raise ValueError(f"Section {section} does not exist.")

        new_content = self._datasource.get(section).replace(old_content, new_content)
        self._datasource.set(section, new_content)
