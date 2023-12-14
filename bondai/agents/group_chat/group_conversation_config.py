from typing import Dict, List, Set
from abc import ABC, abstractmethod
from bondai.agents import ConversationMember


class BaseGroupConversationConfig(ABC):
    @property
    @abstractmethod
    def members(self) -> List[ConversationMember]:
        pass

    @abstractmethod
    def get_reachable_members(
        self, member: ConversationMember | None = None, member_name: str = None
    ) -> List[ConversationMember]:
        pass


class GroupConversationConfig(ABC):
    def __init__(self, members: List[ConversationMember]):
        self._members: Set[ConversationMember] = list(set(members))

    @property
    def _members(self) -> List[ConversationMember]:
        return list(self._members)

    def get_reachable_members(
        self, member: ConversationMember | None = None, member_name: str = None
    ) -> List[ConversationMember]:
        if not member and not member_name:
            return []

        member_name = "" if not member_name else member_name
        reachable_members = list(
            set(
                [
                    m
                    for m in self._members
                    if m != member and m.name.lower() != member_name.lower()
                ]
            )
        )

        return reachable_members


class TeamConversationConfig(BaseGroupConversationConfig):
    def __init__(self, *args: List[ConversationMember]):
        self._members: Set[ConversationMember] = set()
        for team in args:
            self._members.update(team)
        self._teams: List[List[ConversationMember]] = list(args)

    @property
    def members(self) -> List[ConversationMember]:
        return list(self._members)

    def get_reachable_members(
        self, member: ConversationMember | None = None, member_name: str = None
    ) -> List[ConversationMember]:
        if not member and not member_name:
            return []

        member_name = "" if not member_name else member_name
        member_teams = [
            t
            for t in self._teams
            for m in t
            if m == member or m.name.lower() == member_name.lower()
        ]
        reachable_members = list(
            set(
                [
                    m
                    for t in member_teams
                    for m in t
                    if m != member and m.name.lower() != member_name.lower()
                ]
            )
        )

        return reachable_members


class TableConversationConfig(BaseGroupConversationConfig):
    def __init__(self, member_table: Dict):
        self._member_table = member_table

    @property
    def members(self) -> List[ConversationMember]:
        return list(self._member_table.keys())

    def get_reachable_members(
        self, member: ConversationMember | None = None, member_name: str = None
    ) -> List[ConversationMember]:
        if not member and not member_name:
            return []

        if member_name:
            member = next((m for m in self.members if m.name == member_name), None)

        if member and member.name in self._member_table:
            return self._member_table[member.name]
        else:
            return []


class CompositeConversationConfig(BaseGroupConversationConfig):
    def __init__(self, *conversation_configs: List[BaseGroupConversationConfig]):
        self._conversation_configs: List[BaseGroupConversationConfig] = list(
            conversation_configs
        )

    @property
    def members(self) -> List[ConversationMember]:
        return list(set([m for c in self._conversation_configs for m in c.members]))

    def get_reachable_members(
        self, member: ConversationMember | None = None, member_name: str = None
    ) -> List[ConversationMember]:
        return list(
            set(
                [
                    m
                    for c in self._conversation_configs
                    for m in c.get_reachable_members(member, member_name)
                ]
            )
        )
