// /app/test/test.client.tsx
import { useState, useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import Loader from '@/components/ui/loader';
import React from 'react';

const SimpleChat = () => {
  const [messages, setMessages] = useState<string[]>([`Hello! I'm BondAI's helpful and friendly AI Task Assistant.\n\nHow can I assist you today?`]);
  const [steps, setSteps] = useState<string[]>();
  const [agentState, setAgentState] = useState<string>("");
  const [ws, setWs] = useState<Socket<any, any> | null>(null);
  const [isButtonDisabled, setButtonDisabled] = useState<boolean>(true);
  const [textAreaValue, setTextAreaValue] = useState<string>("");

  useEffect(() => {
    const initializeSocket = async () => {
      const socket = await io('ws://localhost:2663', {
        transports: ['websocket'],
      });

      socket.on('agent_started', () => {
        console.log('Agent has started.');
      });
      socket.on('agent_completed', () => {
        console.log('Agent has completed.');
      });
      socket.on('agent_step_completed', (data) => {
        console.log('Agent step completed with data:', data);
      });
      socket.on('connect', () => {
        console.log('Successfully connected to the server.');
      });
      socket.on('disconnect', () => {
        console.log('websocket disconnected.');
      });
      socket.on('message', (response) => {
        const res = JSON.parse(response);
        console.log('Message received:', res);
        if (res.event == 'agent_message') {
          setMessages(prevMessages => [...prevMessages, res.data.message]);

        } else if (res.event == 'agent_step_completed' && !res.data.step.message) {
          setSteps(res.data.step.output);

        } else if (res.event == 'agent_completed') {
          setAgentState('Completed');

        } else if (res.event == 'agent_started') {
          setAgentState('AGENT_STATE_RUNNING');

        } else {
          setMessages(prevMessages => [...prevMessages, res.event]);
        }

      });
      socket.on('connect_error', (error) => {
        console.log('Connection Error:', error);
      });
      socket.on('reconnect', (attempt) => {
        console.log('WebSocket reconnected. Attempt:', attempt);
      });
      socket.on('reconnect_attempt', (attempt) => {
        console.log('Attempting to reconnect. Attempt:', attempt);
      });
      socket.on('reconnect_failed', () => {
        console.log('Reconnection Failed');
      });
      socket.on('reconnect_error', (error) => {
        console.log('Reconnection Error:', error);
      });
      socket.on('agent_message', (msg) => {
        console.log('Received:', msg);
      });
  
      setWs(socket);
  
      await startAgent();
      getAgentState();
  
      return () => {
        socket.disconnect();
      };
    };

    initializeSocket();
  }, []);

  const renderAgentState = (condition: String) => {
    return (
      <div className='flex items-center'>Agent: 
        { 
          (() => {
            switch (condition) {
              case 'AGENT_STATE_RUNNING':
                return (
                  <span className='flex items-center ml-2'>
                    <Loader />
                    Running
                  </span>
                );
              case 'thinking':
                return (
                  <span className='flex items-center ml-2'>
                    <Loader />
                    Thinking..
                  </span>
                );
              case 'AGENT_STATE_STOPPED':
                return (
                  <span>
                    Stopped
                  </span>
                );
              case 'agent_completed':
                return (
                  <span>
                    Completed
                  </span>
                );
              default:
                return (
                  <span>
                    {condition}
                  </span>
                );
            }
          })()
        }
      </div>
    );
  }

  const getAgentState = async () => {
    const apiAgentState = await fetch('http://localhost:2663/agent');
    const agentStateRes = await apiAgentState.json();
    
    if (agentStateRes.state === 'AGENT_STATE_RUNNING') {
      setButtonDisabled(false);
    } else {
      setButtonDisabled(true);
    }
    
    console.log("getAgentState:", agentStateRes.state); 
    setAgentState(agentStateRes.state);
  }

  const startAgent = async () => {
    const apiStartAgent = await fetch('http://localhost:2663/agent/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ })
    })
    const startAgentRes = await apiStartAgent.json()
    console.log('startAgentRes:', startAgentRes);
  }

  const sendMessageToAgent = (message: string) => {
    console.log('sendMessageToAgent:', message);
    setMessages(prevMessages => [...prevMessages, "User: " + message]);
    if (ws) {
      ws.emit('message', {
        'event': 'user_message',
        'data': { message }
      } );
    }
    setTextAreaValue('');
    setAgentState('Thinking');
  };

  const formatMessage = (message: string) => {
    if (!message)
      return
    return message.split('\n').map((line, index) => <React.Fragment key={index}>{line}<br/></React.Fragment>);
  }

  return (
    <div className='flex h-full m-5'>
      <div className='w-3/4 h-full flex flex-col'>
        <h1 className='font-bold text-xl mb-4'>New Task</h1>
        <div className='flex flex-col flex-1 mt-5'>
          <ul className='text-sm font-normal font-mono overflow-y-auto max-h-screen'>
            {messages.map((message, index) => (
              <li className='mb-4' key={index}>{formatMessage(message)}</li>
            ))}
          </ul>
          <textarea
            placeholder='Send a message.'
            className='
              mt-4
              space-y-4 
              border-t 
              bg-background 
              px-4 py-2 
              shadow-lg 
              sm:rounded
              sm:border 
              md:py-4
              text-sm
              '
            value={textAreaValue} 
            onChange={event => setTextAreaValue(event.target.value)}
          ></textarea>
          <button 
            className='
            bg-background 
            border
            hover:bg-white/20
            text-white 
            text-xs 
            py-2 px-3 mt-2 
            rounded'
            onClick={() => sendMessageToAgent(textAreaValue)}
            disabled={isButtonDisabled}
          >
            Send Message
          </button>
        </div>
      </div>
      <div className='w-1/4 bg-black/20 fixed border-l right-0 p-2 overflow-auto' style={{ height: 'calc(100vh - 64px)', top: '64px' }}>
        {/* Your right column contents go here */}
        <div className='flex-grow'>
          <h2 className='text-sm flex items-center'>{renderAgentState(agentState)}</h2>
          <ul className=''>
            {steps?.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SimpleChat;