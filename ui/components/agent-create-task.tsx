// ui/components/agent-send-chat.tsx
import React, { useEffect, useState } from 'react';
import { AgentCreateTaskProps } from '@/lib/agent-types';


export const AgentCreateTask = ({
  agent,
  agentId,
  textareaRef,
  setMessages,
  setIsAgentWorking,
  ws,
  budgetValue,
  maxStepsValue,
} : AgentCreateTaskProps) => {

  const sendMessageToAgent = async (message: string) => {
    setMessages((prevMessages: any) => [...prevMessages, 'User: ' + message]);
    setIsAgentWorking(true);

    if (ws) {
      message += ' [My budget is: ' + budgetValue + '] ';
      message += ' [The maximum number of steps is: ' + maxStepsValue + '] ';
      ws.emit('message', {
        'event': 'user_message',
        'data': {
          'agent_id': agent?.agent_id, 
          message
        }
      });
      console.log(`Sending message to agent ${agent?.agent_id}`, message);
    }
    //clearTextAreaValue();
  };

  return (
  <>
    <textarea
      id='taskbox'
      ref={textareaRef}
      placeholder='Write task'
      className='resize-none hide-scrollbar mt-4 space-y-4 bg-black/70 p-4 shadow-sm dark:shadow-lg border text-black dark:text-white placeholder-black dark:placeholder-white text-sm  focus:outline-none'
      ></textarea>
    <button 
      className='hover:bg-white/20 bg-black/70 border  text-xs shadow-sm dark:shadow-lg py-2 px-3 mt-2 text-black dark:text-white rounded'
      onClick={() => {
        const taskInput = document.getElementById('taskbox') as HTMLInputElement;
        sendMessageToAgent(taskInput?.value);
      }}>
      Create Task
    </button>
  </>
  )
}