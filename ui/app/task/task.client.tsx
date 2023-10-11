// /app/task/task.client.tsx
import { useState, useEffect, useCallback, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import Loader from '@/components/ui/loader';
import React, {ChangeEvent} from 'react';
import { toast } from 'react-hot-toast';

interface ResType {
  data: any;
  event: string;
}

interface MsgObject {
  data: {
    step: {
      error: string;
      exit: string;
      function: {
        arguments: {
          append: boolean,
          filename: string,
          text: string,
          thought: string
        },
        name: string
      };
      message: string;
      output: string;
    }
  },
  event: string;
}

interface RenderAgentEvent {
  agent_message: string;
  messageType: string;
}

interface ButtonProps {
  messageTool: string;
  escapedString: string;
  messageTooltip: {
    filename: string;
  };
}

const ButtonPanel = ({messageTool, escapedString, messageTooltip}: ButtonProps) => {

  const [isTooltipVisible, setTooltipVisibility] = useState(false);

  const handleDownload = (fileName: string) => {
    const url = `/api/download?fileName=${encodeURIComponent(fileName)}`;
    window.open(url, '_blank');
  };

  const toggleTooltip = () => {
    setTooltipVisibility(!isTooltipVisible);
  };

  return (
    <>
      <div className='pt-3 flex justify-end items-end'>
        {messageTooltip?.filename &&
        <button 
          onClick={() => handleDownload(messageTooltip?.filename)} 
          className="glass text-xs font-mono mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300 dark:hover:bg-white/20"
        >
          Download File
        </button>
        }
        <button 
          className="glass text-xs font-mono mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300 dark:hover:bg-white/20"
          onClick={toggleTooltip}>
          {messageTool}
          <span className="toggleSymbol"> {isTooltipVisible ? '-' : '+'}</span>
        </button>
      </div>
      <div className={`${isTooltipVisible ? '' : 'hidden'} w-full tooltip mt-2 p-3 w-100 bg-black/50 text-white rounded z-20`}>
        <pre className="whitespace-pre-wrap">
          {escapedString}
        </pre>
      </div>
    </>
  )
};

const SimpleChat = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [steps, setSteps] = useState<string[]>();
  const [agentState, setAgentState] = useState<string>('');
  const [ws, setWs] = useState<Socket<any, any> | null>(null);
  const [isButtonDisabled, setButtonDisabled] = useState<boolean>(false);
  const [budgetValue, setBudgetValue] = useState<string>('0.00');
  const [maxStepsValue, setMaxStepsValue] = useState<string>('');
  const [isAgentWorking, setIsAgentWorking] = useState(false);
  
  const handleAgentStarted = useCallback(() => {
    setAgentState('AGENT_STATE_RUNNING');
  }, []);

  const handleAgentCompleted = useCallback(() => {
    setAgentState('AGENT_STATE_COMPLETED');
  }, []);

  const handleSocketMessage = useCallback(async(response: string) => {
    const res = JSON.parse(response);
    console.log('Message received:', res.event);

    if (res.event === 'agent_message') {
      console.log('agent_message', res);
      setMessages(prevMessages => [...prevMessages, response]);
      setButtonDisabled(false);
      setIsAgentWorking(false);

    } else if (res.event === 'agent_step_completed') {
      console.log('agent_step_completed', res);
      res.data?.step ? setMessages(prevMessages => [...prevMessages, response]) : null;
      res.data?.step?.function?.name ? setSteps(prevMessages => [...prevMessages || [], res.data.step.function.name]) : null;

    } else if (res.event === 'agent_completed') {
      console.log('agent_completed', res);
      setSteps(prevMessages => [...prevMessages || [], 'Completed']);

    } else if (res.event === 'agent_started') {
      console.log('agent_started', res);
      setSteps(prevMessages => [...prevMessages || [], 'Started']);

    } else {
      console.log('agent uknown', res);
      setMessages(prevMessages => [...prevMessages, response]);
    }
    const agentStateRes = await getAgentState();
    if (agentStateRes) {
      setAgentState(agentStateRes.state);
    }
  }, []);

  const getAgentState = async () => {
    try {
      const res = await fetch('http://localhost:2663/agent');
      if (res.ok) {
        const getAgentState = await res.json();
        //console.log("getAgentState:", getAgentState.state);
        return getAgentState;
      } else {
        console.error(`HTTP Error: ${res.status}`);
      }
    } catch (error: any) {
      console.log('Cannot get agent status:', error.message);
      setAgentState('AGENT_STATE_STOPPED');
      setButtonDisabled(true);
    }
  };
  
  const startAgent = async () => {
    try {
      const res = await fetch('http://localhost:2663/agent/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });
      const startAgent = await res.json();
      console.log('startAgent:', startAgent);
      return startAgent;
    } catch (error: any) {
      console.log('Cannot start agent:', error.message);
      setAgentState('AGENT_STATE_STOPPED');
      setButtonDisabled(true);
    }
  };

  useEffect(() => {
    const init = async () => {
      await startAgent();
      const agentStateRes = await getAgentState();
      if (agentStateRes) {
        setAgentState(agentStateRes.state);
        console.log('Starting Agent:', agentStateRes.state);
      }
      setBudgetValue(localStorage.getItem('budget') || '0.00');
      setMaxStepsValue(localStorage.getItem('maxSteps') || '');
    }
    init();
  }, []);

  useEffect(() => {
    const socket = io('ws://localhost:2663', {
      transports: ['websocket'],
    });

    console.log('Registering socket handlers');

    socket.on('agent_started', () => {
      console.log('agent_started event received');
      handleAgentStarted();
    });

    socket.on('agent_completed', handleAgentCompleted);
    socket.on('message', handleSocketMessage);

    setWs(socket);

    return () => {
      socket.off('agent_started', handleAgentStarted);
      socket.off('agent_completed', handleAgentCompleted);
      socket.off('message', handleSocketMessage);
      socket.disconnect();
    };
  }, [handleAgentStarted, handleAgentCompleted, handleSocketMessage]);

  const sendMessageToAgent = async (message: string) => {
    console.log('sendMessageToAgent:', message);
    setMessages(prevMessages => [...prevMessages, 'User: ' + message]);
    setIsAgentWorking(true);

    if (ws) {
      message += ' [My budget is: ' + budgetValue + '] ';
      message += ' [The maximum number of steps is: ' + maxStepsValue + '] ';
      ws.emit('message', {
        'event': 'user_message',
        'data': { message }
      } );
    }
    setButtonDisabled(true);
    clearTextAreaValue();
  };

  const renderAgentState = (condition: string): string => {
    let stateText;

    switch (condition) {
      case 'AGENT_STATE_RUNNING':
        stateText = 'Active';
        break;
      case 'AGENT_STATE_STOPPED':
        stateText = 'Stopped';
        break;
      default:
        stateText = condition;
        break;
    }
    return `Agent ${stateText}`;
  };

  const renderAgentEvent = (condition: string): string => {
    switch (condition) {
      case 'agent_message':
      case 'agent_step_completed':
        return 'AGENT';
      default:
        return condition;
    }
  };

  function isJSON(str: string) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
  }

  const convertObjectToString = (obj: any): string => {
    let str = '';
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'object' && value !== null) {
        str += `${key.charAt(0).toUpperCase() + key.slice(1)}: \n${convertObjectToString(value)}\n`;
      } else {
        str += `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}\n`;
      }
    }
    return str.trim();
  };

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
      // console.log('formatMessage: message:', message);
      // console.log('formatMessage: messageTool:', messageTool);
      // console.log('formatMessage: messageTooltip:', messageTooltip);
      // console.log('formatMessage: messageType:', messageType);

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
      <div className='card mb-4 text-white text rounded p-4 border border-gray-500 shadow-xl'>                  
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

  const formatStep = (message: string) => {
    if (!message) return null;
    const formattedMessage = message.replace(/_/g, ' ').toUpperCase();
    return <span className='px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 mb-2'>{formattedMessage}</span>
  };

  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const stepsEndRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    stepsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, steps]);

  const setBudget = () => {
    localStorage.setItem('budget', budgetValue);
    toast.success('Budget set!');
  };

  const handleBudgetChange = (e: ChangeEvent<HTMLInputElement>) => {
    setBudgetValue(e.target.value);
  };

  const setMaxSteps = () => {
    localStorage.setItem('maxSteps', maxStepsValue);
    toast.success('Max Steps set!');
  };

  const handleMaxStepsChange = (e: ChangeEvent<HTMLInputElement>) => {
    setMaxStepsValue(e.target.value);
  };

  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  const handleInput = () => {
    if (textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'inherit';
      textarea.style.height = `${textarea.scrollHeight}px`;  
    }
  };

  React.useEffect(() => {
    const handleResize = () => {
      handleInput();
    };
  
    // Bind the event listener
    window.addEventListener("resize", handleResize);
  
    // Unbind the event listener on clean up
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const clearTextAreaValue = () => {
    const messageElement = document.getElementById('message') as HTMLInputElement;
    messageElement.value = '';
  };

  useEffect(() => {
    const handleScroll = () => {
      const cards = Array.from(document.querySelectorAll('.card'));

      let lastVisibleCard;
      for (let card of cards){
        const rect = card.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.80){
          lastVisibleCard = card;
        } else {
          break;
        }
      }
      
      cards.forEach(card => {
        card.classList.remove('bg-gradient-to-r');
        card.classList.remove('from-indigo-500/20');
        card.classList.remove('via-purple-500/10');
        card.classList.remove('to-pink-500/10');
        card.classList.add('card-gradient');
      })
  
      if(lastVisibleCard) {
        lastVisibleCard.classList.add('bg-gradient-to-r');
        lastVisibleCard.classList.add('from-indigo-500/20');
        lastVisibleCard.classList.add('via-purple-500/10');
        lastVisibleCard.classList.add('to-pink-500/10');
        lastVisibleCard.classList.remove('card-gradient');
      }
  
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <>
      <div className='flex h-full m-5'>
        {/* left column */}
        <div className='w-3/4 max-w-[600px] h-full flex flex-col'>
          <h1 className='font-bold text-xl mb-4'>New Task</h1>
          <div className='flex flex-col flex-1 mt-5'>
            <ul className='text-sm font-normal'>
              <li className='mb-4'>
                Hello! I'm BondAI's helpful and friendly AI Task Assistant.
              </li>
              <li className='mb-4'>
                How can I assist you today?
              </li>
              {messages.map((message, index) => (
                <li className='mb-4' key={index}>
                  {formatMessage(message)}
                </li>
              ))}
              {isAgentWorking && (
                <div className="card card-gradient mb-4 text-white text rounded p-4 border border-gray-500 shadow-xl">                  
                  <div className="card-body">
                    <h2 className="card-title mb-4">
                    <span className="glass text-xs font-medium mr-2 px-2.5 py-0.5 rounded dark:text-white border border-white dark:border-gray-300">AGENT</span>
                    </h2>
                    <div className='flex items-center'><Loader color='white' /> Working</div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </ul>
            <textarea
              id='message'
              ref={textareaRef}
              placeholder='Send a message.'
              className='
                resize-none
                hide-scrollbar
                mt-4
                space-y-4 
                bg-background/50 
                p-4
                shadow-sm 
                dark:shadow-lg 
                border 
                text-black dark:text-white
                placeholder-black
                dark:placeholder-white
                text-sm
                focus:outline-none
                '
              onChange={handleInput}
            ></textarea>
            <button 
              className='
              bg-background/50 
              border
              hover:bg-white/20
              text-xs 
              shadow-sm
              dark:shadow-lg 
              py-2 px-3 mt-2 
              text-black dark:text-white
              rounded
              '
              onClick={() => {
                const messageElement = document.getElementById('message') as HTMLInputElement;
                sendMessageToAgent(messageElement?.value);
              }}
              disabled={isButtonDisabled}
            >
              Send Message
            </button>

            <div className='flex flex-col sm:flex-row justify-between mt-10'>

              <div className='flex items-center mb-5'>
                <div className='relative text-gray-400 focus-within:text-gray-600 inline'>
                  <div className='text-sm text-black dark:text-white py-1.5 pointer-events-none w-8 h-8 absolute top-1/2 transform -translate-y-1/2 left-3'>$</div>
                  <input 
                    type='number' 
                    className='
                      w-[110px]
                      bg-background/50 
                      mr-2 
                      pl-6 pr-4 py-1.5
                      shadow-sm 
                      dark:shadow-lg 
                      rounded
                      border
                      text-black dark:text-white
                      text-sm
                    '
                    value={budgetValue} 
                    onChange={handleBudgetChange} 
                  />
                </div>
                <button 
                  className='
                    w-auto
                    bg-background/50 
                    border
                    hover:bg-white/20
                    shadow-sm 
                    dark:shadow-lg 
                    text-xs 
                    py-2 px-3
                    mr-2
                    rounded
                    text-black dark:text-white
                    whitespace-nowrap
                  '
                  onClick={() => setBudget()}
                >
                  Set Max Budget
                </button>
              </div>

              <div className='flex items-center mb-5'>
                <input 
                  type='number' 
                  className='
                    w-[110px]
                    bg-background/50 
                    mr-2 
                    pl-6 pr-4 py-1.5
                    shadow-sm
                    dark:shadow-lg 
                    border
                    rounded
                    text-black dark:text-white
                    text-sm
                  '
                  value={maxStepsValue} 
                  onChange={handleMaxStepsChange} 
                />
                <button 
                  className='
                    w-auto
                    bg-background/50 
                    border
                    hover:bg-white/20
                    shadow-sm 
                    dark:shadow-lg 
                    text-xs 
                    py-2 px-3
                    rounded
                    text-black dark:text-white
                    whitespace-nowrap
                  '
                  onClick={() => setMaxSteps()}
                >
                  Set Max Steps
                </button>
              </div>
              
            </div>
          </div>
        </div>

        {/* right column */}
        <div className='text-black dark:text-white w-1/4 dark:bg-black/20 fixed border-l right-0 p-2' style={{ height: 'calc(100vh - 64px)', top: '64px' }}>
          <div className='flex-grow'>
            <h2 className='mb-4 flex items-center'>
              <div className='text-sm'>
                {renderAgentState(agentState)} 
              </div>
              {agentState === 'AGENT_STATE_RUNNING' && (
                <span className="relative flex h-3 w-3 ml-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
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
              <div ref={stepsEndRef} />
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};

export default SimpleChat;