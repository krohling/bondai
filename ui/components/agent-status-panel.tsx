// ui/components/agent-status-panel.tsx
import React, { useRef, useState, useEffect } from 'react';
import { Loader } from '@/components/ui/loader';
import AgentStatus from '@/components/ui/agent-status';
import { AgentStatusProps } from '@/lib/agentTypes';
import { readConversationFromFile } from '@/lib/agentFileStorage';

interface MessageInterface {
  data?: {
    step?: {
      function?: {
        name?: string;
      };
    };
  },
  event: string
}

const AgentStatusPanel = ({ 
  steps,
  setSteps,
  isAgentWorking, 
  agentState,
  setAgentState,
  agents,
  agentId,
  agentWorkingMessage,
}: AgentStatusProps) => {
  const stepsEndRef = React.createRef<HTMLLIElement>();

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
        stateText = '';
        break;
    }
    return `${stateText}`;
  };

  const formatStep = (message: string) => {
    if (!message) return null;
    const formattedMessage = message.replace(/_/g, ' ').toUpperCase();

    if (formattedMessage == 'STARTED' || formattedMessage == 'COMPLETED') {
      return <span className='px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 mb-2'>{formattedMessage}</span>
    
    } else if (formattedMessage == 'SELECTING TOOL') {
      return <span className='px-2 ml-3 inline-flex text-xs leading-5 font-semibold rounded-full bg-transparent border border-gray-500 text-gray-500 mb-2'>{formattedMessage}</span>
    
    } else {
      return <span className='px-2 ml-3 inline-flex text-xs leading-5 font-semibold rounded-full bg-violet-100 text-violet-900 mb-2'>{formattedMessage}</span>
    }
  };

  useEffect(() => {
    const agent = agents?.find(a => a.agent_id === agentId);
    if (agent) {
      setAgentState(agent.state);
    }
  }, [agents, agentId]);

  // Load saved steps when component mounts
  useEffect(() => {
    const loadSteps = async () => {
      const response = await readConversationFromFile(agentId);
      if (response?.ok) {
        const conversationData = await response.json();
        if (conversationData && conversationData.messages) {  
          const stepsArray: any[] = [];

          conversationData.messages.forEach((message: MessageInterface) => {
            if (message.event === 'task_agent_started') {
              stepsArray.push('Started');

            } else if (message.event === 'task_agent_completed') {
              stepsArray.push('Completed');

            } else if (message.event === 'task_agent_step_tool_selected') {
              stepsArray.push('Selecting Tool');
              stepsArray.push(message?.data?.step?.function?.name);
            }
          });
    
          setSteps(stepsArray);
        }
      } else {
        console.log(`Failed to load steps: ${response?.status}`);
      }
    };
    loadSteps();
  }, []);

  /*
  <li>
  <div class="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -left-1.5 border border-white dark:border-gray-900 dark:bg-gray-700"></div>
    <time class="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">February 2022</time>
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Application UI code in Tailwind CSS</h3>
    <p class="mb-4 text-base font-normal text-gray-500 dark:text-gray-400">
      Get access to over 20+ pages including a dashboard layout, charts, kanban board, 
      calendar, and pre-order E-commerce & Marketing pages.</p>
    <a href="#" class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:outline-none focus:ring-gray-200 focus:text-blue-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 dark:focus:ring-gray-700">
      Learn more 
      <svg class="w-3 h-3 ml-2" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5h12m0 0L9 1m4 4L9 9"/>
      </svg>
    </a>
    </li>
    */
 
  return (
    <>
    {agentId && (
      <div className='flex-grow p-4'>
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
        <ul className='text-xs'>
          {steps?.map((step, index) => (
            <li key={index}>{formatStep(step)}</li>
          ))}
          {isAgentWorking && (
            <li key={`loader-${agentId}`}>
              <div className='flex items-center'>
                <Loader color='white' /> {agentWorkingMessage} {isAgentWorking}
              </div>
            </li>
          )}
          <li key={`anchor-${agentId}`} ref={stepsEndRef} className='pb-40'></li>
        </ul>
      </div>
    )}
    </>
  );
};

export default AgentStatusPanel;