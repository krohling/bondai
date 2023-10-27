// ui/components/agent-tabs.tsx
export const AgentTabSettings = () => {
  return <div>Inactive Agent</div>;
};
    
export const AgentTabChat = () => {
  return <div>Active Agent</div>;
};

interface AgentContainerProps {
  tab: string;
}

export const AgentStateContainer: React.FC<AgentContainerProps> = ({ tab }) => {
  if (tab === 'SETTINGS') {
    return <AgentTabSettings />;
  } else if (tab === 'CHAT') {
    return <AgentTabChat />;
  } else {
    return <div></div>;
  }
};