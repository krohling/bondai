from typing import Dict, List, Set
from abc import ABC, abstractmethod
from ..conversation_member import ConversationMember

class GroupConversationConfig(ABC):
    @property
    @abstractmethod
    def members(self) -> List[ConversationMember]:
        pass

    @abstractmethod
    def get_reachable_members(self, 
                            member: ConversationMember | None = None, 
                            member_name: str = None
                        ) -> List[ConversationMember]:
        pass


class TeamConversationConfig(GroupConversationConfig):

    def __init__(self, *args: List[List[ConversationMember]]):
        self._agents: Set[ConversationMember] = set()
        for team in args:
            self._agents.update(team)
        self._teams: List[List[ConversationMember]] = list(args)
    
    @property
    def members(self) -> List[ConversationMember]:
        return list(self._agents)

    def get_reachable_members(self, 
                                member: ConversationMember | None = None, 
                                member_name: str = None
                            ) -> List[ConversationMember]:
        member_name = '' if not member_name else member_name
        agent_teams = [t for t in self._teams for a in t if a == member or a.name.lower() == member_name.lower()]
        reachable_members = list(set([a for t in agent_teams for a in t if a != member and a.name.lower() != member_name.lower()]))

        return reachable_members

class TableConversationConfig(GroupConversationConfig):

    def __init__(self, agent_table: Dict):
        self._agent_table = agent_table
    
    @property
    def members(self) -> List[ConversationMember]:
        return list(self._agent_table.keys())

    def get_reachable_members(self, 
                                member: ConversationMember | None = None, 
                                member_name: str = None
                            ) -> List[ConversationMember]:
        if not member:
            member = next((a for a in self.members if a.name == member_name), None)

        return self._agent_table[member.name]

class CompositeConversationConfig(GroupConversationConfig):

    def __init__(self, *conversation_configs: List[GroupConversationConfig]):
        self._conversation_configs: List[GroupConversationConfig] = list(conversation_configs)
    
    @property
    def members(self) -> List[ConversationMember]:
        return list(set([a for c in self._conversation_configs for a in c.agents]))

    def get_reachable_members(self, 
                                member: ConversationMember | None = None, 
                                member_name: str = None
                            ) -> List[ConversationMember]:
        return list(set([a for c in self._conversation_configs for a in c.get_reachable_members(member, member_name)]))