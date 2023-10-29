// ui/components/agent-status-panel.tsx
import React, { useRef, useState, useEffect } from 'react';
import { Loader } from '@/components/ui/loader';
import AgentStatus from '@/components/ui/agent-status';
import { AgentStatusProps } from '@/lib/agent-types';


const AgentStatusPanel = ({ 
  steps, 
  isAgentWorking, 
  agentState,
  setAgentState,
  stepsEndRef,
  agents,
  agentId,
}: AgentStatusProps) => {

  const renderAgentState = (condition: string): string => {
    let stateText;

    switch (condition) {
      case 'AGENT_STATE_RUNNING':
        stateText = 'Agent Active';
        break;
      case 'AGENT_STATE_STOPPED':
        stateText = 'Agent Stopped';
        break;
      default:
        stateText = condition;
        break;
    }
    return `${stateText}`;
  };

  const formatStep = (message: string) => {
    if (!message) return null;
    const formattedMessage = message.replace(/_/g, ' ').toUpperCase();
    return <span className='px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 mb-2'>{formattedMessage}</span>
  };

  useEffect(() => {
    const agent = agents?.find(a => a.agent_id === agentId);
    if (agent) {
      setAgentState(agent.state);
    }
  }, [agents, agentId]);

  //console.log("agent-status-panel: agentState: ", agentState);
 
  return (
    <>
      <div className='min-w-[250px] w-[250px] flex-grow fixed border-l right-0 p-4' style={{ height: 'calc(100vh - 64px)', top: '64px' }}>
        <h2 className='mb-4 flex items-center'>
          <div className='text-sm'>
            {renderAgentState(agentState)} 
          </div>
          {agentState === 'AGENT_STATE_RUNNING' ? (
            <AgentStatus status='active' /> 
          ) : agentState && (
            <AgentStatus status='inactive' /> 
          )}
        </h2>
        <ul className='text-xs overflow-y-auto max-h-screen custom-scrollbar'>
          {steps?.map((step, index) => (
            <li key={index}>{formatStep(step)}</li>
          ))}
          {isAgentWorking && (
            <li>
              <div className='flex items-center'>
                <Loader color='white' /> Working
              </div>
            </li>
          )}
          <li className='pb-40'></li>
          <div ref={stepsEndRef}></div>
        </ul>
      </div>
    </>
  );
};

export default AgentStatusPanel;