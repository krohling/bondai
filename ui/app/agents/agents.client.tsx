// /app/agents/agents.client.tsx
import { useState, useEffect, useCallback, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import React from 'react';
import AgentChatPanel from '@/components/agent-chat-panel';
import AgentStatusPanel from '@/components/agent-status-panel';
import AgentListPanel from '@/components/agent-list-panel';
import AgentDashboard from '@/components/agent-dashboard';
import { AgentProps } from '@/lib/agentTypes';
import { saveConversationToFile } from '@/lib/agentFileStorage';

const AgentChat = ({ 
  agents,
  agentId,
  refreshAgents
  }: AgentProps) => {

  const [messages, setMessages] = useState<string[]>([]);
  const [steps, setSteps] = useState<string[]>([]);
  const [agentState, setAgentState] = useState<string>('');
  const [ws, setWs] = useState<Socket<any, any> | null>(null);
  const [isAgentStarted, setIsAgentStarted] = useState<boolean>(false);
  const [isAgentWorking, setIsAgentWorking] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState('task');
  const [agentWorkingMessage, setAgentWorkingMessage] = useState<string>('Working');
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
    //console.log(res.event, res);
    
    if (res.event === 'conversational_agent_started') {
      console.log('conversational_agent_started', res);
      setAgentState('AGENT_STATE_RUNNING');

    } else if (res.event === 'conversational_agent_message') {
      console.log('conversational_agent_message', res);
      setMessages(prevMessages => [...prevMessages, response]);
      setIsAgentWorking(false);
      setIsAgentStarted(true);

    } else if (res.event === 'agent_message') {
      console.log('agent_message', res);
      setMessages(prevMessages => [...prevMessages, response]);
      setIsAgentWorking(false);

    } else if (res.event === 'task_agent_step_started') {
      console.log('task_agent_step_started', res);
      setAgentWorkingMessage('Working out First Step');

    } else if (res.event === 'task_agent_step_tool_selected') {
      console.log('task_agent_step_tool_selected', res);
      res.data?.step ? setMessages(prevMessages => [...prevMessages, response]) : null;
      res.data?.step?.function?.name ? setSteps(prevMessages => [...prevMessages || [], 'Selecting Tool']) : null;
      res.data?.step?.function?.name ? setSteps(prevMessages => [...prevMessages || [], res.data.step.function.name]) : null;
      setAgentWorkingMessage('Selecting Tool');

    } else if (res.event === 'task_agent_step_completed') {
      console.log('task_agent_step_completed', res);
      res.data?.step ? setMessages(prevMessages => [...prevMessages, response]) : null;
      setAgentWorkingMessage('Step Completed');

    } else if (res.event === 'task_agent_completed') {
      console.log('task_agent_completed', res);
      setSteps(prevMessages => [...prevMessages || [], 'Completed']);
      setAgentWorkingMessage('Task Completed');

    } else if (res.event === 'task_agent_started') {
      console.log('task_agent_started', res);
      setSteps(prevMessages => [...prevMessages || [], 'Started']);
      setAgentWorkingMessage('Starting Task');

    } else {
      console.log('agent unknown', res);
    }
    
    saveConversationToFile(res);
  }, []);

  useEffect(() => {
    const socket = io('ws://localhost:2663', {
      transports: ['websocket'],
      rejectUnauthorized: false,
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

    socket.on("connect_error", (err) => {
      console.log(`connect_error due to ${err.message}`);
    });

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
      <div className="flex flex-grow HIDE:dark:bg-black/70 HIDE:bg1 max-h-screen" style={{ height: 'calc(100vh - 64px)', top: '64px' }}>

        <div id="agents-panel" className='min-w-[220px] w-[220px] text-black dark:text-white dark:bg-black/40 px-1 py-2 overflow-y-auto custom-scrollbar'>
          <AgentListPanel
            agentId={agentId}
            agents={agents}
            refreshAgents={refreshAgents || (() => Promise.resolve())}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            agentState={agentState}
            setAgentState={setAgentState}
          />
        </div>

        <div id="chat-panel" className="flex-grow p-5 sm:p-3 max-w-[800px] min-w-[450px] overflow-y-auto custom-scrollbar">
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
                setSteps={setSteps}
                agents={agents}
                agentId={agentId}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                isAgentStarted={isAgentStarted}
                setIsAgentStarted={setIsAgentStarted}
                agentState={agentState}
                setAgentState={setAgentState}
                agentWorkingMessage={agentWorkingMessage}
                setAgentWorkingMessage={setAgentWorkingMessage}
              />
            ) : (
              <AgentDashboard
                agents={agents}
                refreshAgents={refreshAgents || (() => Promise.resolve())}              
              />
            )
          }
        </div>

        <div id="status-panel" className='min-w-[250px] w-[250px] text-black dark:text-white px-3 py-2 overflow-y-auto custom-scrollbar'>
          <AgentStatusPanel
            steps={steps}
            setSteps={setSteps}
            isAgentWorking={isAgentWorking}
            agentState={agentState}
            setAgentState={setAgentState}
            stepsEndRef={stepsEndRef}
            agents={agents}
            agentId={agentId}
            agentWorkingMessage={agentWorkingMessage}
          />
        </div>

      </div>
    </>
  );
};

export default AgentChat;