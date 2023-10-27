// ui/components/agent-dashboard.tsx
import React, { useState, useEffect } from 'react';
import Link from 'next/link';

type Agent = {
  agent_id: string;
  name: string;
};

interface AgentListProps {
  agents: Agent[] | null;
  refreshAgents: () => Promise<void>;
}

const AgentDashboard = ({ agents: initialAgents, refreshAgents }: AgentListProps) => {
  const [agents, setAgents] = useState<Agent[] | null>(initialAgents);

  useEffect(() => {
    setAgents(initialAgents);
  }, [initialAgents]);

  return (
    <div>
      <h1 className='font-bold text-xl mb-4'>Agent Dashboard</h1>
      <div className="flex justify-center items-center">
        <div className="flex flex-wrap mt-5 w-full justify-center">
          {
            agents?.map((agent, index) => (
              <div key={index} className="flex-none m-2">
                <Link key={index} href={`/agents/${agent.agent_id}`} className="flex items-center justify-center border border-white/5 bg-black/50 hover:bg-white/5 shadow-lg p-4 w-28 h-28">
                  <div className="flex flex-col items-center">
                    <span className="text-2xl mb-2">🤖</span>
                    <span className="text-sm">{agent.name}</span>
                  </div>
                </Link>
              </div>
            ))
          }
        </div>
      </div>
      {
        // !agents && (
        //   <div className='text-sm text-gray-500'>Such emptyness. Let's create a new agent!</div>
        // )
      }
    </div>
  )
}

export default AgentDashboard;