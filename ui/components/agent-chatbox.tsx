// ui/components/agent-send-chat.tsx
import React, { useEffect, useState } from 'react';
import { AgentChatBoxProps } from '@/lib/agent-types';
import { saveConversationToFile, readConversationFromFile } from '@/lib/agentFileStorage';


export const AgentChatBox = ({
  agent,
  textareaRef,
  setMessages,
  messages,
  setIsAgentWorking,
  isAgentStarted,
  agentState,
  ws,
  budgetValue,
  maxStepsValue,
} : AgentChatBoxProps) => {

  const clearTextAreaValue = () => {
    const messageElement = document.getElementById('message') as HTMLInputElement;
    messageElement.value = '';
    messageElement.focus();
  };

  const handleInput = () => {
    if (textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'inherit';
      textarea.style.height = `${textarea.scrollHeight}px`;  
    }
  };

  useEffect(() => {
    const handleResize = () => {
      handleInput();
    };
    
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const sendMessageToAgent = async (message: string) => {
    setMessages((prevMessages: any) => [...prevMessages, 'User: ' + message]);

    setIsAgentWorking(true);

    if (ws) {
      const msgPayload = {
        'event': 'user_message',
        'data': { 
          'agent_id': agent?.agent_id,
          message 
        }
      }
      ws.emit('message', msgPayload);

      saveConversationToFile(msgPayload);

      console.log(`Sending message to agent ${agent?.agent_id}`, message);
    }
    clearTextAreaValue();
  };

  return (
    <>
    {agentState === 'AGENT_STATE_RUNNING' && (
      <>
      <textarea
        id='message'
        ref={textareaRef}
        placeholder='Send a message.'
        className='resize-none hide-scrollbar mt-4 space-y-4 bg-black/70 p-4 shadow-sm dark:shadow-lg border text-black dark:text-white placeholder-black dark:placeholder-white text-sm  focus:outline-none'
        onChange={handleInput}></textarea>
      <button 
        className='bg-black/70 border hover:bg-white/20 text-xs shadow-sm dark:shadow-lg py-2 px-3 mt-2 text-black dark:text-white rounded'
        onClick={() => {
          const messageElement = document.getElementById('message') as HTMLInputElement;
          sendMessageToAgent(messageElement?.value);
        }}
        >
        Send Message
      </button>
      </>
    )}
    </>
  )
}