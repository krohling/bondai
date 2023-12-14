import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict

DEFAULT_MEMORY_SECTIONS = {
    "task": "",
    "user": "",
}


class CoreMemoryDataSource(ABC):
    @property
    @abstractmethod
    def sections(self) -> List[str]:
        pass

    @abstractmethod
    def get(self, section: str) -> str:
        pass

    @abstractmethod
    def set(self, section: str, content: str) -> None:
        pass


class PersistentCoreMemoryDataSource(CoreMemoryDataSource):
    def __init__(
        self,
        file_path: str = "./.memory/core-memory.json",
        sections: Dict[str, str] | None = None,
        max_section_size: int = 1024,
    ):
        if sections is None:
            sections = DEFAULT_MEMORY_SECTIONS.copy()
        self._file_path = file_path
        self._max_section_size = max_section_size
        self._data = self._load_data(sections)

    def _load_data(self, initial_sections: Dict[str, str] = None):
        try:
            with open(self._file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return initial_sections if initial_sections else {}

    def _save_data(self):
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        with open(self._file_path, "w") as file:
            json.dump(self._data, file, indent=4)

    @property
    def sections(self) -> List[str]:
        return list(self._data.keys())

    def get(self, section: str) -> str:
        return self._data.get(section, "")

    def set(self, section: str, content: str) -> None:
        if len(content) > self._max_section_size:
            raise ValueError(
                f"Content exceeds maximum allowed size of {self._max_section_size} characters."
            )
        self._data[section] = content
        self._save_data()


class InMemoryCoreMemoryDataSource(CoreMemoryDataSource):
    def __init__(
        self, sections: Dict[str, str] | None = None, max_section_size: int = 1024
    ):
        if sections is None:
            sections = DEFAULT_MEMORY_SECTIONS.copy()
        self._max_section_size = max_section_size
        self._data = sections.copy()

    @property
    def sections(self) -> List[str]:
        return list(self._data.keys())

    def get(self, section: str) -> str:
        return self._data.get(section, "")

    def set(self, section: str, content: str) -> None:
        if len(content) > self._max_section_size:
            raise ValueError(
                f"Content exceeds maximum allowed size of {self._max_section_size} characters."
            )
        self._data[section] = content
