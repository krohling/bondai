// ui/lib/agent-types.ts
import React from 'react';
import { type Socket } from 'socket.io-client';

export type Agents = {
  agent_id: string;
  name: string;
  state: string;
  previous_messages: string[];
};

export type Agent = {
  agent_id: string;
  name: string;
  state: string;
  previous_messages: string[];
};

export interface AgentChatProps {
  isAgentWorking: boolean;
  setMessages: (prevMessages: any) => void;
  messages: { [key: string]: string[] }
  setIsAgentWorking: (boolean: boolean) => void;
  ws: Socket<any, any> | null;
  steps: string[] | undefined;
  setSteps: (prevMessages: any) => void;
  agents: Agents[] | null;
  agentId: string | undefined;
  activeTab: string;
  setActiveTab: (string: string) => void;
  isAgentStarted: boolean;
  setIsAgentStarted: (boolean: boolean) => void;
  agentState: string;
  setAgentState: (string: string) => void;
  agentWorkingMessage: string;
  setAgentWorkingMessage: (string: string) => void;
}

export type AgentProps = {
  agents: Agents[] | null;
  agentId?: string;
  refreshAgents?: () => Promise<void>;
}

export interface AgentListProps {
  agentId?: string;
  agents: Agents[] | null;
  refreshAgents: () => Promise<void>;
  activeTab: string;
  setActiveTab: (string: string) => void;
  agentState: string;
  setAgentState: (string: string) => void;
}

export interface AgentPageProps {
  params: {
    id: string;
  };
}

export interface AgentTabProps {
  budgetValue: string;
  handleBudgetChange: string; 
  setBudget: (string: string) => void;
  maxStepsValue: string;
  handleMaxStepsChange: string;
  setMaxSteps: (string: string) => void;
}

export interface AgentBudgetProps {
  budgetValue: string;
  setBudgetValue: (value: string) => void;
  maxStepsValue: string;
  setMaxStepsValue: (value: string) => void;
}

export interface AgentStatusProps {
  steps: string[] | undefined;
  setSteps: (prevMessages: any) => void;
  isAgentWorking: boolean;
  agentState: string;
  setAgentState: (string: string) => void;
  stepsEndRef: React.RefObject<HTMLDivElement>;
  agents: Agents[] | null;
  agentId: string | undefined;
  agentWorkingMessage: string;
}

export interface AgentChatBoxProps {
  agent: Agent | undefined;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  setMessages: (prevMessages: any) => void;
  messages: { [key: string]: string[] }
  setIsAgentWorking: (isWorking: boolean) => void;
  isAgentWorking: boolean;
  isAgentStarted: boolean;
  ws: Socket<any, any> | null;
  budgetValue: string;
  maxStepsValue: string;
  agentState: string;
  setAgentWorkingMessage: (message: string) => void;
}

export interface AgentCreateTaskProps {
  agent: Agent | undefined;
  agentId?: string;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  setMessages: (prevMessages: any) => void;
  setIsAgentWorking: (boolean: boolean) => void;
  ws: Socket<any, any> | null;
  budgetValue: string;
  maxStepsValue: string;
}

export interface AgentChatStageProps {
  messages: { [key: string]: string[] }
  setMessages: (prevMessages: any) => void;
  isAgentWorking: boolean;
  steps: string[] | undefined;
  setSteps: (prevMessages: any) => void;
  agentId?: string;
  agentWorkingMessage: string;
  setAgentWorkingMessage: (string: string) => void;
}



