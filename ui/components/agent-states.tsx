// ui/components/agent-states.tsx
export const AgentStateInactive = () => {
  return <div>Inactive Agent</div>;
};
  
export const AgentStateActive = () => {
  return <div>Active Agent</div>;
};

interface AgentContainerProps {
  state: string;
}

export const AgentStateContainer: React.FC<AgentContainerProps> = ({ state }) => {
  if (state === 'INACTIVE') {
    return <AgentStateInactive />;
  } else if (state === 'ACTIVE') {
    return <AgentStateActive />;
  } else {
    return <div>Unknown State</div>;
  }
};