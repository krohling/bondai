// ui/components/agent-chat-stage.tsx
import React, { useRef, useEffect } from 'react';
import { AgentChatStageProps } from '@/lib/agent-types';
import { Loader } from '@/components/ui/loader';
import { isJSON, convertObjectToString } from '@/lib/utils';
import ButtonPanel from '@/components/agent-button-panel';
import { saveConversationToFile, readConversationFromFile } from '@/lib/agentFileStorage';

export const AgentChatStage = ({
  messages,
  setMessages,
  isAgentWorking,
  agentId,
} : AgentChatStageProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const formatMessage = (msgData: any) => {
    const regexBudget = / \[My budget is: \d+\.?\d*\]/;
    const regexSteps = / \[The maximum number of steps is:.*?\]/;
    let message: any | null = null;
    let messageType: string | null = null;
    let messageTool: string | undefined = undefined;
    let messageTooltip: any;
    let buttonPanel: JSX.Element | null = null;
    let escapedString: string | null = null;

    if (isJSON(msgData)) {
      msgData = JSON.parse(msgData);

      if (msgData.data.message) {
        message = msgData.data.message;
      } else if (msgData.data?.step?.message) {
        message = msgData.data?.step?.message;
      } else {
        message = msgData.data?.step?.output;
      }
      messageTool = msgData.data?.step?.function?.name.replace(/_/g, ' ').toUpperCase();

      if (messageTool) {
        messageTooltip = msgData.data?.step?.function?.arguments ?? '';
        escapedString = convertObjectToString(messageTooltip);
        buttonPanel = <ButtonPanel messageTool={messageTool} escapedString={escapedString} messageTooltip={messageTooltip} />
      }

      messageType = msgData.event;

    } else {
      message = msgData?.replace(regexBudget, '').replace(regexSteps, '');
    }

    if (message?.includes('User:')) {
      return <span className="text-white dark:text-blue-400">{message}</span>;
    }

    if (message?.includes('\n')) {
      message = message.split('\n').map((line: string, index: number) => <>{line}<br/></>);
    }

    if (!messageType) {
      return <span className="">Uknown Message Type: {message}</span>
    }

    return (
      <div className='card mb-4 text-white text rounded p-4 border border-gray-500 shadow-xl card-gradient'>                  
        <div className='card-body'>
          <h2 className='card-title mb-4'>
            <span className='glass text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-500'>{renderAgentEvent(messageType)}</span>
          </h2>
          <p className='text-sm leading-5'>{message}</p>
          {buttonPanel}
        </div>
      </div>
    )
  };

  const renderAgentEvent = (condition: string): string => {
    switch (condition) {
      case 'agent_message':
      case 'conversational_agent_message':
      case 'conversational_agent_start':
      case 'agent_step_completed':
      case 'task_agent_step_completed':
        return 'AGENT';
      default:
        return condition;
    }
  };

  // Load saved messages when component mounts
  useEffect(() => {
    const loadMessages = async () => {
      const response = await readConversationFromFile(agentId);
      if (response.ok) {
        const conversationData = await response.json();
        if (conversationData && conversationData.messages) {  
          const transformedMessages = conversationData.messages.map((msg: any) => {
            if (msg.event === "user_message") {
              return `User: ${msg.data.message}`;
            } else {
              return JSON.stringify(msg);
            }
          });
          setMessages(transformedMessages);
        }
      } else {
        console.log(`Failed to load messages: ${response.status}`);
      }
    };
    loadMessages();
  }, []);


  console.log("messages loop", messages)
  return (
  <>
    <ul className='text-sm font-normal'>

      {messages?.map((message, index) => (
        <li className='mb-4' key={index}>
        {formatMessage(message)}
        </li>
      ))}

      {isAgentWorking && (
      <li key={`9998-${agentId}`}>
        <div className="card card-gradient mb-4 text-white text rounded p-4 border border-gray-500 shadow-xl">                  
          <div className="card-body">
            <h2 className="card-title mb-4">
              <span className="glass text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300">AGENT</span>
            </h2>
            <div className='flex items-center'><Loader color='white' /> Working</div>
          </div>
        </div>
      </li>
      )}

      <li key={`9999-${agentId}`} ref={messagesEndRef}></li>
    </ul>
  </>
  )
}