import os
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from bondai.agents.messages import (
    AgentMessage,
    AgentMessageList,
    ConversationMessage,
    SystemMessage,
    ToolUsageMessage,
)


def format_messages(messages: List[AgentMessage]) -> str:
    results = []
    for message in messages:
        if isinstance(message, ConversationMessage) or isinstance(
            message, SystemMessage
        ):
            results.append(message.message)
        elif isinstance(message, ToolUsageMessage):
            results.append(message.tool_output)
    return "\n".join(results)


class ConversationMemoryDataSource(ABC):
    @property
    @abstractmethod
    def messages(self) -> List[AgentMessage]:
        pass

    @abstractmethod
    def add(self, message: AgentMessage):
        pass

    @abstractmethod
    def remove(self, message: AgentMessage):
        pass

    def remove_after(self, timestamp: datetime, inclusive: bool = True):
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        start_date: datetime = None,
        end_date: datetime = None,
        page: int = 0,
    ) -> List[str]:
        pass

    @abstractmethod
    def clear(self):
        pass


class InMemoryConversationMemoryDataSource(ConversationMemoryDataSource):
    def __init__(self, page_size=10):
        self._page_size = page_size
        self._data = AgentMessageList()

    @property
    def messages(self) -> List[AgentMessage]:
        return self._data

    def add(self, message: AgentMessage):
        self._data.add(message)

    def remove(self, message: AgentMessage):
        self._data.remove(message)

    def remove_after(self, timestamp: datetime, inclusive: bool = True):
        self._data.remove_after(timestamp, inclusive=inclusive)

    def search(
        self,
        query: str,
        start_date: datetime = None,
        end_date: datetime = None,
        page: int = 0,
    ) -> List[AgentMessage]:
        print(f"Searching for '{query}' in messages from {start_date} to {end_date}")
        results = []
        for message in self._data:
            if (not start_date or message.timestamp >= start_date) and (
                not end_date or message.timestamp <= end_date
            ):
                if (
                    (
                        isinstance(message, ConversationMessage)
                        or isinstance(message, SystemMessage)
                    )
                    and message.message
                    and query.lower() in message.message.lower()
                ):
                    results.append(message)
                elif (
                    isinstance(message, ToolUsageMessage)
                    and message.tool_output
                    and query.lower() in message.tool_output.lower()
                ):
                    results.append(message)

        # Implementing a simple pagination
        start_index = page * self._page_size
        end_index = start_index + self._page_size
        result = format_messages(results[start_index:end_index])
        # print(result)
        return result

    def clear(self):
        self._data.clear()


class PersistentConversationMemoryDataSource(InMemoryConversationMemoryDataSource):
    def __init__(
        self, file_path: str = "./.memory/conversation-memory.json", page_size=10
    ):
        InMemoryConversationMemoryDataSource.__init__(self, page_size=page_size)
        self._file_path = file_path
        self._data = AgentMessageList.from_dict(self._load_data())

    def _load_data(self):
        try:
            with open(self._file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def _save_data(self):
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        with open(self._file_path, "w") as file:
            json.dump(self._data.to_dict(), file, indent=4)

    def add(self, message: str) -> None:
        super().add(message)
        self._save_data()

    def remove(self, message: str) -> None:
        super().remove(message)
        self._save_data()

    def remove_after(self, timestamp: datetime, inclusive: bool = True):
        super().remove_after(timestamp, inclusive=inclusive)
        self._save_data()

    def clear(self):
        super().clear()
        self._save_data()
