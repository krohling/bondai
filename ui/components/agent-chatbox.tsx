// ui/components/agent-send-chat.tsx
import React, { useEffect } from 'react';
import { AgentChatBoxProps } from '@/lib/agentTypes';
import { saveConversationToFile } from '@/lib/agentFileStorage';
import { toast } from 'react-hot-toast';

export const AgentChatBox = ({
  agent,
  textareaRef,
  setMessages,
  setIsAgentWorking,
  isAgentWorking,
  agentState,
  ws,
  setAgentWorkingMessage,
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

    if (isAgentWorking) {
      toast.success('Agent is working..');
      return;
    }

    setIsAgentWorking(true);
    setAgentWorkingMessage('Working');

    if (ws) {
      const msgPayload = {
        'event': 'user_message',
        'data': { 
          'agent_id': agent?.agent_id,
          message 
        }
      }
      ws.emit('message', msgPayload);
      //setMessages((prevMessages: any) => [...prevMessages, msgPayload]);

      const agent_id: any = agent?.agent_id;
      setMessages((prevMessages: { [x: string]: any; }) => {
        let agentMessages = [...(prevMessages[agent_id] || []), msgPayload];
        return { ...prevMessages, [agent_id]: agentMessages };
      });
      saveConversationToFile(msgPayload);
      console.log(`Sending message to agent ${agent?.agent_id}`, message);
    }
    clearTextAreaValue();
  };

  return (
    <>
    {agentState === 'AGENT_STATE_RUNNING' && (
      <div className='max-w-[600px] flex flex-col w-full'>
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
      </div>
    )}
    </>
  )
}