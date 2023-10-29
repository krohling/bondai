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
  setIsAgentWorking: (boolean: boolean) => void;
  ws: Socket<any, any> | null;
  steps: string[] | undefined;
  agents: Agents[] | null;
  agentId: string | undefined;
  activeTab: string;
  setActiveTab: (string: string) => void;
  isAgentStarted: boolean;
  setIsAgentStarted: (boolean: boolean) => void;
  agentState: string;
  setAgentState: (string: string) => void;
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
  setBudget: (string: string) => void;
  maxStepsValue: string;
  setMaxSteps: (string: string) => void;
}

export interface AgentStatusProps {
  steps: string[] | undefined;
  isAgentWorking: boolean;
  agentState: string;
  setAgentState: (string: string) => void;
  stepsEndRef: React.RefObject<HTMLDivElement>;
  agents: Agents[] | null;
  agentId: string | undefined;
}

export interface AgentChatBoxProps {
  agent: Agent | undefined;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  setMessages: (prevMessages: any) => void;
  messages: string[] | undefined;
  setIsAgentWorking: (boolean: boolean) => void;
  isAgentStarted: boolean;
  ws: Socket<any, any> | null;
  budgetValue: string;
  maxStepsValue: string;
  agentState: boolean;
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
  messages: string[] | undefined;
  setMessages: (prevMessages: any) => void;
  isAgentWorking: boolean;
  agentId?: string;
}



