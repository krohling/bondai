// /app/agents/agents.client.tsx
import { useState, useEffect, useCallback, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import React from 'react';
import AgentChatPanel from '@/components/agent-chat-panel';
import AgentStatusPanel from '@/components/agent-status-panel';
import AgentListPanel from '@/components/agent-list-panel';
import AgentDashboard from '@/components/agent-dashboard';
import { AgentProps } from '@/lib/agent-types';
import { saveConversationToFile, readConversationFromFile } from '@/lib/agentFileStorage';

const AgentChat = ({ 
  agents,
  agentId,
  refreshAgents
  }: AgentProps) => {

  const [messages, setMessages] = useState<string[]>([]);
  const [steps, setSteps] = useState<string[]>();
  const [agentState, setAgentState] = useState<string>('');
  const [ws, setWs] = useState<Socket<any, any> | null>(null);
  const [isAgentStarted, setIsAgentStarted] = useState<boolean>(false);
  const [isAgentWorking, setIsAgentWorking] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState('task');
  // const [refreshState, setRefreshState] = useState(0);
  const stepsEndRef = useRef<HTMLDivElement>(null);

  const handleAgentStarted = useCallback(() => {
    setAgentState('AGENT_STATE_RUNNING');
    console.log('AGENT_STATE_RUNNING');
  }, []);

  const handleAgentCompleted = useCallback(() => {
    setAgentState('AGENT_STATE_COMPLETED');
    console.log('AGENT_STATE_COMPLETED');
  }, []);

  const handleSocketMessage = useCallback(async(response: string) => {
    const res = JSON.parse(response);
    console.log('Message received:', res.event);

    
    if (res.event === 'conversational_agent_started') {
      console.log('conversational_agent_started', res);

    } else if (res.event === 'conversational_agent_message') {
      console.log('conversational_agent_message', res);
      const agent_id = res.data.agent_id;
      setMessages(prevMessages => [...prevMessages, response]);
      saveConversationToFile(res);
      setIsAgentWorking(false);
      setIsAgentStarted(true);
      setAgentState('AGENT_STATE_RUNNING');

    } else if (res.event === 'agent_message') {
      console.log('agent_message', res);
      setMessages(prevMessages => [...prevMessages, response]);
      setIsAgentWorking(false);

    } else if (res.event === 'task_agent_step_completed') {
      console.log('task_agent_step_completed', res);
      res.data?.step ? setMessages(prevMessages => [...prevMessages, response]) : null;
      res.data?.step?.function?.name ? setSteps(prevMessages => [...prevMessages || [], res.data.step.function.name]) : null;

    } else if (res.event === 'task_agent_completed') {
      console.log('task_agent_completed', res);
      setSteps(prevMessages => [...prevMessages || [], 'Completed']);

    } else if (res.event === 'task_agent_started') {
      console.log('task_agent_started', res);
      setSteps(prevMessages => [...prevMessages || [], 'Started']);

    } else {
      console.log('agent uknown', res);
      //setMessages(prevMessages => [...prevMessages, response]);
    }
    /* END OLD */
  }, []);

  useEffect(() => {
    const socket = io('ws://localhost:2663', {
      transports: ['websocket'],
    });

    console.log('Registering socket handlers');

    socket.on('conversational_agent_started', () => {
      console.log('agent_started event received');
      handleAgentStarted();
    });

    socket.on('agent_completed', handleAgentCompleted);
    socket.on('message', handleSocketMessage);
    socket.on('conversational_agent_message', handleSocketMessage);

    setWs(socket);

    return () => {
      socket.off('agent_started', handleAgentStarted);
      socket.off('agent_completed', handleAgentCompleted);
      socket.off('message', handleSocketMessage);
      socket.disconnect();
    };
  }, [handleAgentStarted, handleAgentCompleted, handleSocketMessage]);

  // useEffect(() => {
  //   if (isAgentStarted) {
  //     setRefreshState(prevState => prevState + 1);
  //   }
  // }, [isAgentStarted]);

  return (
    <>
      <div className="flex flex-grow HIDE:dark:bg-black/70 HIDE:bg1">

        <div id="agents-panel" className='min-w-[200px] w-[200px] text-black dark:text-white dark:bg-black/40 px-3 py-5'>
          <AgentListPanel
            agentId={agentId}
            agents={agents}
            refreshAgents={refreshAgents || (() => Promise.resolve())}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            agentState={agentState}
          />
        </div>

        <div id="chat-panel" className="flex-grow m-3 p-5 sm:p-3">
          {
            /* Conditionally render AgentChatPanel based on the URL */
            agentId ? (
              <AgentChatPanel 
                setMessages={setMessages}
                messages={messages}
                isAgentWorking={isAgentWorking}
                setIsAgentWorking={setIsAgentWorking}
                ws={ws}
                steps={steps}
                agents={agents}
                agentId={agentId}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                isAgentStarted={isAgentStarted}
                setIsAgentStarted={setIsAgentStarted}
                agentState={agentState}
                setAgentState={setAgentState}
              />
            ) : (
              <AgentDashboard
                agents={agents}
                refreshAgents={refreshAgents || (() => Promise.resolve())}              
              />
            )
          }
        </div>

        <div id="status-panel" className='min-w-[250px] w-[250px] text-black dark:text-white px-3 py-5'>
          <AgentStatusPanel
            steps={steps}
            isAgentWorking={isAgentWorking}
            agentState={agentState}
            setAgentState={setAgentState}
            stepsEndRef={stepsEndRef}
            agents={agents}
            agentId={agentId}
          />
        </div>

      </div>
    </>
  );
};

export default AgentChat;