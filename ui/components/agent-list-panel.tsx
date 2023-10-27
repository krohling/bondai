// ui/components/agent-list-panel.tsx
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { getAgentName } from '@/lib/utils';
import { Agent, AgentListProps } from '@/lib/agent-types';


const AgentListPanel = ({ 
  agentId,
  agents: initialAgents, refreshAgents,
  activeTab,
  setActiveTab,
  agentState
}: AgentListProps) => {
  const [agents, setAgents] = useState<Agent[] | null>(initialAgents);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  if (agents && agents.length > 0) {
    console.log("AgentListPanel agents", agents);
  }

  useEffect(() => {
    setAgents(initialAgents);
  }, [initialAgents]);

  const handleTabClick = (tab: string) => {
    setActiveTab(tab);
  };

  const createAgent = async () => {

    try {
      const res = await fetch('http://localhost:2663/agents', {
        method: 'POST'
      });
      const newAgent = await res.json();
      console.log('newAgent:', newAgent, typeof newAgent);
      const newAgentNamed = {
        ...newAgent,
        name: getAgentName(newAgent.agent_id),
      };

      if (agents) {
        setAgents([...agents, newAgentNamed]);
      } else {
        setAgents([newAgentNamed]);
      }
      await refreshAgents();
      
      console.log('createAgent:', newAgent);
      return createAgent;

    } catch (error: any) {
      console.log('Cannot create agent:', error);
    }
  };

  useEffect(() => {
    setLastRefreshed(new Date());
  }, [agentState]);

  return (
    <div className='flex-grow'>
      <h2 className='text-sm mb-4 flex items-center'>
        Agents
      </h2>

      <button 
        className='bg-background/50 border hover:bg-white/20 text-xs shadow-sm dark:shadow-lg py-2 px-3 mr-2 text-black dark:text-white rounded flex-start'
        onClick={() => {
          createAgent();
        }}
      >
        Create
      </button>
      {
        window?.location?.pathname != '/agents' && 
        <Link 
          href={`/agents/`}
          className='inline-block bg-background/50 border hover:bg-white/20 text-xs shadow-sm dark:shadow-lg py-2 px-3 text-black dark:text-white rounded flex-start'
        >
          Dashboard
        </Link>
      }

      <ul className='text-sm mt-5'>
        {agents?.map((agent, index) => (
          <li key={index}>
            <Link href={`/agents/${agent.agent_id}`}>
              <h2 className='mb-1 flex items-center hover:bg-white/5 p-2'>

              {agent.state === 'AGENT_STATE_RUNNING' || (agentState === 'AGENT_STATE_RUNNING' && agent.agent_id === agentId) ? (
                <>
                <span className="relative flex h-3 w-3 mr-3">
                  <span className="relative inline-flex rounded-full h-3 w-3 border-2 border-green-500 bg-transparent"></span>
                </span>
                <span className={(agent.agent_id === agentId) ? 'font-bold' : 'text-slate-500'}>{agent.name}</span>
                </>
              ) : (
                <>
                <span className="relative flex h-3 w-3 mr-3">
                  <span className="relative inline-flex rounded-full h-3 w-3 border-2 border-slate-500 bg-transparent"></span>
                </span>
                <span className={(agent.agent_id === agentId) ? 'font-bold' : 'text-slate-300'}>{agent.name}</span>
                </>
              )}

              </h2>
            </Link>
            {agent.agent_id === agentId ? (
              <ul className="ml-8 text-xs">
                <li className='pb-2'>
                  <button
                    onClick={() => handleTabClick('task')}
                    className={`inline-block hover:text-gray-600 dark:hover:text-gray-300 ${activeTab === 'task' ? 'dark:text-blue-400 border-blue-400' : 'text-gray-500 dark:text-gray-400'}`}
                    role="tab"
                    aria-controls="task"
                    aria-selected={activeTab === 'task'}>
                    Task
                  </button>
                </li>
                <li className='pb-2'>
                  <button
                    onClick={() => handleTabClick('settings')}
                    className={`inline-block hover:text-gray-600 dark:hover:text-gray-300 ${activeTab === 'settings' ? 'dark:text-blue-400 border-blue-400' : 'text-gray-500 dark:text-gray-400'}`}
                    role="tab"
                    aria-controls="settings"
                    aria-selected={activeTab === 'settings'}>
                    Settings
                  </button>
                </li>
                <li className='pb-2'>
                  <button
                    onClick={() => handleTabClick('tools')}
                    className={`inline-block hover:text-gray-600 dark:hover:text-gray-300 ${activeTab === 'tools' ? 'dark:text-blue-400 border-blue-400' : 'text-gray-500 dark:text-gray-400'}`}
                    role="tab"
                    aria-controls="tools"
                    aria-selected={activeTab === 'tools'}>
                    Tools
                  </button>
                </li>
                <li className='pb-2'>
                  <button
                    onClick={() => handleTabClick('team')}
                    className={`inline-block hover:text-gray-600 dark:hover:text-gray-300 ${activeTab === 'team' ? 'dark:text-blue-400 border-blue-400' : 'text-gray-500 dark:text-gray-400'}`}
                    role="tab"
                    aria-controls="team"
                    aria-selected={activeTab === 'team'}>
                    Team
                  </button>
                </li>
              </ul>
            ) : null}
          </li>
        ))}
      </ul>

      {agentState === 'AGENT_STATE_RUNNING' && ( 
        <>
          <div className='hidden text-xs font-light text-white/30 mt-6'>
            Refreshed: 
            <div>
              {lastRefreshed.toLocaleString()}
            </div>
          </div>
        </>
      )}

      {/*
      <ul className='text-sm mt-5'>
        {agents?.map((agent, index) => (
          <li key={index}>
            <Link key={index} href={`/agents/${agent.agent_id}`}>
              <h2 className='mb-1 flex items-center hover:bg-white/5 p-2'>
                <span className="relative flex h-3 w-3 mr-3">
                  <span className="relative inline-flex rounded-full h-3 w-3 border-2 border-slate-500 bg-transparent"></span>
                </span>
                {agent.name}
              </h2>
            </Link>
          </li>
        ))}
      </ul>
    */}
    </div>
  );
};

export default AgentListPanel;
