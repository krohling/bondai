// lib/useAgents.ts
import { useState, useEffect } from 'react';
import { getAgentName } from '@/lib/utils';

const useAgents = () => {
  const [agents, setAgents] = useState<any[]>([]);
  const [error, setError] = useState(null);

  const getAgentsAPI = async () => {
    try {
      const res = await fetch('http://localhost:2663/agents', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const fetchedAgents = await res.json();
      const agentList = fetchedAgents.map((agent: { agent_id: string; }) => {
        return {
          ...agent,
          name: getAgentName(agent.agent_id),
        };
      });
      // console.log('getAgents:', agentList);
      setAgents(agentList);
    } catch (error: any) {
      console.log('Cannot get agents:', error.message);
      setError(error.message);
    }
  };

  useEffect(() => {
    getAgentsAPI();
  }, []);

  return { agents, error, getAgentsAPI };
};

export default useAgents;
