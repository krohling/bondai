// ui/components/agent-chat-stage.tsx
import React, { useEffect } from 'react';
import { AgentChatStageProps } from '@/lib/agentTypes';
import { Loader } from '@/components/ui/loader';
import { isJSON, convertObjectToString } from '@/lib/utils';
import ButtonPanel from '@/components/agent-button-panel';
import { readConversationFromFile } from '@/lib/agentFileStorage';

interface ToolDataProps {
  toolName: string;
  toolInput: string;
  toolQuery: string;
  toolThought: string;
  toolTotalCost: string;
}

interface MsgPayloadProps {
  eventType: string;
  message: string;
  totalCost: string;
  toolName: string;
  arguments?: {
    query: string;
    thought: string;
    input: string;
  };
  buttonPanel?: JSX.Element | null;
  selectingTool?: boolean;
}

interface ItemProps {
  message: string;
  index: number; 
}

export const AgentChatStage = ({
  messages,
  setMessages,
  setSteps,
  steps,
  isAgentWorking,
  agentId,
  agentWorkingMessage,
  setAgentWorkingMessage,
} : AgentChatStageProps) => {
  const messagesEndRef = React.createRef<HTMLLIElement>();
  const stepsEndRef = React.createRef<HTMLLIElement>();
  let messageTool: string | undefined = undefined;
  let messageTooltip: any;
  let buttonPanel: JSX.Element | null = null;
  let escapedString: string | null = null;
  let eventType: string;
  let pushMessage: React.ReactNode;
  let msgPayload: MsgPayloadProps;
  let toolPayload: ToolDataProps;
  let compiledMsg: React.ReactNode[] = [];
  let compiledTool: JSX.Element | null = null;
  let elements: React.ReactNode[] = [];

  function processMessage(msgData: any): React.ReactNode {

    msgData = isJSON(msgData) ? JSON.parse(msgData) : msgData;
    eventType = msgData.event;
    messageTool = msgData.data?.step?.function?.name.replace(/_/g, ' ').toUpperCase() ?? '';
    compiledMsg = [];
    elements = [];
    
    msgPayload = {
      eventType: eventType,
      message: msgData.data?.message ?? '',
      totalCost: msgData.data?.step?.total_cost ?? '',
      toolName: msgData.data?.step?.function?.name.replace(/_/g, ' ').toUpperCase() ?? '',
      selectingTool: false,
    }

    toolPayload = {
      toolName: msgData.data?.step?.function.name.replace(/_/g, ' ').toUpperCase() ?? '',
      toolInput: msgData.data?.step?.function.arguments.input?? '',
      toolQuery: msgData.data?.step?.function.arguments.query?? '',
      toolThought: msgData.data?.step?.function.arguments.thought?? '',
      toolTotalCost: msgData.data?.step?.function.arguments.totalCost?? '',
    }

    if (messageTool) {
      messageTooltip = msgData.data?.step?.function?.arguments ?? '';
      escapedString = convertObjectToString(messageTooltip);
      buttonPanel = <ButtonPanel messageTool={messageTool} escapedString={escapedString} messageTooltip={messageTooltip} />
    }

    if (
      eventType == 'task_agent_started' ||
      eventType == 'task_agent_step_started'
    ) {
      return;
    }

    if (eventType == 'conversational_agent_message') {
      pushMessage = formatAgentMessage(msgPayload);
      compiledMsg.push(pushMessage);
    }

    if (eventType == 'user_message') {
      pushMessage = formatUserMessage(msgPayload);
      compiledMsg.push(pushMessage);
    }
    
    if (eventType == 'task_agent_step_tool_selected') {
      msgPayload.message = msgData.data.step.message;
      msgPayload.selectingTool = true;
      pushMessage = formatAgentMessage(msgPayload);
      compiledMsg.push(pushMessage);
      pushMessage = formatToolMessage(toolPayload);
      compiledMsg.push(pushMessage);
    }

    if (eventType == 'task_agent_step_tool_completed') {
      msgPayload.message = msgData.data.step.output;
      pushMessage = formatAgentMessage(msgPayload);
      compiledMsg.push(pushMessage);
    }

    return compiledMsg
  };

  const formatToolMessage = (toolPayload: ToolDataProps) => {
    return (
      <div className='card mb-4 text-white text rounded p-4 border border-gray-500 shadow-xl bg-black/30'>                 
        <div className='card-body'>
          <h2 className='card-title mb-4'>
            <span className='glass text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-500'>
              TOOL - {toolPayload.toolName}
            </span>
          </h2>
          {toolPayload.toolInput ? (
            <div>
              <p className='text-sm leading-5'>Thought: {
              toolPayload.toolInput?.includes('\n')
                ? toolPayload.toolInput.split('\n').map((line: string, index: number) => <React.Fragment key={index}>{line}<br/></React.Fragment>)
                : toolPayload.toolInput}
              </p>
            </div>
          ) : (
            <div>
              <p className='text-sm leading-5'>Query: {toolPayload.toolQuery}</p>
              <p className='text-sm leading-5'>Thought: {toolPayload.toolThought}</p>
            </div>
          )}

          {toolPayload.toolTotalCost && (
            <div className='pt-3 flex justify-end items-end'>
              <div className="glass text-xs font-mono mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300 dark:hover:bg-white/20">
                ${toolPayload.toolTotalCost} USD
              </div>
            </div>
          )}
        </div>
      </div>
    )
  };

  const formatAgentMessage = (payload: MsgPayloadProps) => {
    return (
      <div className='card mb-4 text-white text rounded p-4 border border-gray-500 shadow-xl card-gradient'>                  
        <div className='card-body'>
          <h2 className='card-title mb-4'>
            <span className='glass text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-500'>
              {renderAgentEvent(payload.eventType)}
            </span>
          </h2>
          <p className='text-sm leading-5'>
          {payload.message?.includes('\n')
            ? payload.message.split('\n').map((line: string, index: number) => <React.Fragment key={index}>{line}<br/></React.Fragment>)
            : payload.message}
          </p>
          {payload.buttonPanel}

          <div className='pt-3 flex justify-end items-end'>
            {payload.totalCost && (
              <div className="glass text-xs font-mono mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300 dark:hover:bg-white/20">
                ${payload.totalCost} USD
              </div>
            )}
            {payload.selectingTool && (
              <div className="glass text-xs font-mono mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300 dark:hover:bg-white/20">
                Selecting Tool: {payload.toolName}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  };

  const formatUserMessage = (payload: any) => {
    return (
      <span className="text-white dark:text-blue-400">User: {payload.message}</span>
    )
  };

  const renderAgentEvent = (condition: string): string => {
    switch (condition) {
      case 'agent_message':
      case 'conversational_agent_message':
      case 'conversational_agent_start':
      case 'agent_step_completed':
      case 'task_agent_step_completed':
      case 'task_agent_step_tool_selected':
        return 'AGENT';
      default:
        return condition;
    }
  };

  // Load saved messages when component mounts
  useEffect(() => {
    const loadMessages = async () => {
      const response = await readConversationFromFile(agentId);
      if (response?.ok) {
        const conversationData = await response.json();
        console.log('loadMessages conversationData:', conversationData);
        if (conversationData && conversationData.messages) {  
          const transformedMessages = conversationData.messages.map((msg: any) => {
            return JSON.stringify(msg);
          });
          // setMessages(transformedMessages);
          let agent_id: any = agentId || '';
          let updatedMessages: any[] = [];
          setMessages(() => {
            updatedMessages[agent_id]?.push(transformedMessages);
            return updatedMessages;
          });
        }
      } else {
        console.log(`Failed to load messages: ${response?.status}`);
      }
    };
    loadMessages();
  }, []);

  // Auto scrolling 
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    stepsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, steps]);

  const agentMessages = messages && agentId !== undefined ? messages[agentId] : [];

  console.log('Agent Messages:', agentMessages);

  return (
    <ul className='text-sm font-normal w-full'>

      {agentMessages?.map((message: any, index: React.Key | null | undefined) => (
        <li key={index} className='mb-4'>
          {processMessage(message)}
        </li>
      ))}

      {isAgentWorking && (
      <li key={`working-${agentId}`}>
        <div className="card card-gradient mb-4 text-white text rounded p-4 border border-gray-500 shadow-xl">                  
          <div className="card-body">
            <h2 className="card-title mb-4">
              <span className="glass text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300">AGENT</span>
            </h2>
            <div className='flex items-center'><Loader color='white' /> {agentWorkingMessage}</div>
          </div>
        </div>
      </li>
      )}

      <li key={`anchor-${agentId}`} ref={messagesEndRef}></li>
    </ul>
  )
}