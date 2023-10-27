// app/agents/page.tsx 
"use client"
import React from 'react';
import AgentChat from './agents.client';
import useAgents from '@/lib/useAgents';
import { AgentPageProps } from '@/lib/agent-types';


export default function AgentsPage({}: AgentPageProps) {
  const { agents, getAgentsAPI } = useAgents();

  return (
    <>
      <AgentChat
        agents={agents}
        refreshAgents={getAgentsAPI}
      />
    </>
  );
};
