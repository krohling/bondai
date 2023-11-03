// ui/components/agent-chat-panel.tsx
import React, { useState, useEffect, useRef } from 'react';
import { AgentBudgetSteps } from '@/components/agent-budget-steps';
import { AgentSettings } from '@/components/agent-settings';
import { Loader } from '@/components/ui/loader';
import { AgentChatBox } from '@/components/agent-chatbox';
import { AgentChatStage } from '@/components/agent-chat-stage';
import { AgentChatProps, Agent } from '@/lib/agentTypes';
import { startAgentAPI, stopAgentAPI } from '@/lib/agentActions';

const AgentChatPanel = ({ 
  isAgentWorking,
  setMessages,
  messages,
  setIsAgentWorking,
  ws,
  steps,
  setSteps,
  agents,
  agentId,
  activeTab,
  setActiveTab,
  isAgentStarted,
  setIsAgentStarted,
  agentState,
  setAgentState,
  agentWorkingMessage,
  setAgentWorkingMessage,
 }: AgentChatProps) => {
  const [budgetValue, setBudgetValue] = useState<string>('0.00');
  const [maxStepsValue, setMaxStepsValue] = useState<string>('0');
  const [isStartingAgent, setIsStartingAgent] = useState(false);
  const [isComponentLoaded, setIsComponentLoaded] = useState(false);

  useEffect(() => {
    setIsComponentLoaded(true);
  }, []);

  const handleTabClick = (tab: string) => {
    setActiveTab(tab);
  };

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
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

    //window.addEventListener('scroll', handleScroll);

    return () => {
      //window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const startAgent = async () => {
    console.log("startAgent(): ", agentId);
    setIsStartingAgent(true);
    setIsAgentWorking(true);
    setAgentWorkingMessage('Starting');
    startAgentAPI(agentId, budgetValue, maxStepsValue);
  };

  const stopAgent = async () => {
    console.log("stopAgent(): ", agentId);
    const stopAgentResult = await stopAgentAPI(agentId)
    
    if (stopAgentResult.status == "success") {
      setAgentState('AGENT_STATE_STOPPED');
      setIsAgentWorking(false);
      setIsAgentStarted(false);
    }
  };

  const agent: Agent | undefined = agents?.find(a => a.agent_id === agentId);

  if (!isComponentLoaded) {
    return <div>Loading...</div>;
  }

  if (!agent) {
    return <div>Agent not found.</div>;
  }
  
  return (
    <>
      <div className='flex flex-row justify-between'>
        <div>
          <h1 className='font-bold text-lg mb-3'>🤖 {agent.name}</h1>
        </div>
        <div>
        </div>
      </div>

      <div className='max-w-[1000px] flex flex-col flex-1'>

          <div className="border-b border-gray-200 dark:border-gray-700 mb-4">
            <ul className="flex flex-wrap -mb-px" id="myTab" data-tabs-toggle="#myTabContent" role="tablist">
              <li className="mr-2" role="presentation">
                <button
                  onClick={() => handleTabClick('task')}
                  className={`inline-block hover:text-gray-600 dark:hover:text-gray-300 hover:border-gray-300 rounded-t-lg py-2 px-4 text-sm font-medium text-center border-b-2 ${activeTab === 'task' ? 'dark:text-blue-400 border-blue-400' : 'text-gray-500 dark:text-gray-400 border-transparent'}`}
                  role="tab"
                  aria-controls="task"
                  aria-selected={activeTab === 'task'}>
                  Task
                </button>
              </li>
              <li className="mr-2" role="presentation">
                <button
                  onClick={() => handleTabClick('settings')}
                  className={`inline-block hover:text-gray-600 dark:hover:text-gray-300 hover:border-gray-300 rounded-t-lg py-2 px-4 text-sm font-medium text-center border-b-2 ${activeTab === 'settings' ? 'dark:text-blue-400 border-blue-400' : 'text-gray-500 dark:text-gray-400 border-transparent'}`}
                  role="tab"
                  aria-controls="settings"
                  aria-selected={activeTab === 'settings'}>
                  Settings
                </button>
              </li>
              <li className="mr-2" role="presentation">
                <button
                  onClick={() => handleTabClick('tools')}
                  className={`inline-block hover:text-gray-600 dark:hover:text-gray-300 hover:border-gray-300 rounded-t-lg py-2 px-4 text-sm font-medium text-center border-b-2 ${activeTab === 'tools' ? 'dark:text-blue-400 border-blue-400' : 'text-gray-500 dark:text-gray-400 border-transparent'}`}
                  role="tab"
                  aria-controls="tools"
                  aria-selected={activeTab === 'tools'}>
                  Tools
                </button>
              </li>
              <li className="mr-2" role="presentation">
                <button
                  onClick={() => handleTabClick('team')}
                  className={`inline-block hover:text-gray-600 dark:hover:text-gray-300 hover:border-gray-300 rounded-t-lg py-2 px-4 text-sm font-medium text-center border-b-2 ${activeTab === 'team' ? 'dark:text-blue-400 border-blue-400' : 'text-gray-500 dark:text-gray-400 border-transparent'}`}
                  role="tab"
                  aria-controls="team"
                  aria-selected={activeTab === 'team'}>
                  Team
                </button>
              </li>
            </ul>
          </div>

          <div id="myTabContent">
            {activeTab === 'task' && ( 
              <div role="tabpanel" aria-labelledby="task-tab">

                <div className='flex flex-col flex-1 mt-5 items-center justify-center '>

                  {agentState === 'AGENT_STATE_RUNNING' && (
                    <>
                      <AgentChatStage
                        messages={messages}
                        setMessages={setMessages}
                        isAgentWorking={isAgentWorking}
                        steps={steps}
                        setSteps={setSteps}
                        agentId={agentId}
                        agentWorkingMessage={agentWorkingMessage}
                        setAgentWorkingMessage={setAgentWorkingMessage}
                      />

                      <AgentChatBox
                        agent={agent}
                        textareaRef={textareaRef}
                        setMessages={setMessages}
                        messages={messages}
                        setIsAgentWorking={setIsAgentWorking}
                        isAgentWorking={isAgentWorking}
                        isAgentStarted={isAgentStarted}
                        ws={ws}
                        budgetValue={budgetValue}
                        maxStepsValue={maxStepsValue}
                        agentState={agentState}
                        setAgentWorkingMessage={setAgentWorkingMessage}
                      />
                    </>
                  )}

                  <div className='max-w-[600px] flex flex-col justify-between items-center mt-10 space-y-5 sm:space-y-0 sm:space-x-5'>
                    <div className='flex items-center'>

                      {agentState === 'AGENT_STATE_RUNNING' ? (
                        <div className='bg-black/70 border flex items-center text-xs shadow-sm dark:shadow-lg py-2 px-5 mr-2 text-black dark:text-white/50 rounded'>
                          <span className="relative flex h-3 w-3 mr-1">
                            <span className="relative inline-flex rounded-full h-3 w-3 border-2 border-green-500 bg-transparent"></span>
                          </span> 
                          Agent Active
                        </div>
                      ) : isStartingAgent ? (
                        <div className='bg-black/70 border flex items-center text-xs shadow-sm dark:shadow-lg py-2 px-5 mr-2 text-black dark:text-white rounded'>
                          <Loader color='white' size='xs' /> Agent Starting
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            startAgent()
                          }}
                          className='bg-black/70 border hover:bg-white/20 text-xs shadow-sm dark:shadow-lg py-2 px-5 mr-2 text-black dark:text-white rounded'
                        >
                          ▷ Start Agent
                        </button>
                      )}

                      {agentState === 'AGENT_STATE_STOPPED' ? (
                        <div className='bg-black/70 border flex items-center text-xs shadow-sm dark:shadow-lg py-2 px-5 text-black dark:text-white/50 rounded'>
                          <span className="relative flex h-3 w-3 mr-1">
                            <span className="relative inline-flex rounded-full h-3 w-3 border-2 border-slate-500 bg-transparent"></span>
                          </span> 
                          Agent Stopped
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            stopAgent()
                          }}
                          className='bg-black/70 border hover:bg-white/20 text-xs shadow-sm dark:shadow-lg py-2 px-5 mr-2 text-black dark:text-white rounded'
                        >
                          ☐ Stop Agent
                        </button>
                      )}

                    </div>
                  </div>
                </div>

              </div>
            )}
            {activeTab === 'settings' && ( 
              <div role="tabpanel" aria-labelledby="settings-tab">
                <div className='max-w-[600px] flex flex-col flex-1 mt-5'>
                  <div className='text-sm'>Let's get setup.</div>
                  <AgentSettings/>
                  <AgentBudgetSteps
                    budgetValue={budgetValue} 
                    setBudgetValue={setBudgetValue} 
                    maxStepsValue={maxStepsValue} 
                    setMaxStepsValue={setMaxStepsValue}
                  />
                </div>
              </div>
            )}
            {activeTab === 'tools' && ( 
              <div role="tabpanel" aria-labelledby="tools-tab">
                <div className='max-w-[600px] flex flex-col flex-1 mt-5'>
                  <div className='text-sm'>Tools Setup.</div>
                </div>
              </div>
            )}
            {activeTab === 'team' && ( 
              <div role="tabpanel" aria-labelledby="team-tab">
                <div className='max-w-[600px] flex flex-col flex-1 mt-5'>
                  <div className='text-sm'>Assign your agent to a team.</div>
                </div>
              </div>
            )}
          </div>    

      </div>
    </>
  );
};

export default AgentChatPanel;