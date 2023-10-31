// app/agents/[id]/page.tsx
"use client"
import React from 'react';
import AgentChat from '@/app/agents/agents.client';
import useAgents from '@/lib/useAgents';
import { type AgentPageProps } from '@/lib/agentTypes';

export default function AgentPage({ params }: AgentPageProps) { 
  const agentId = params.id;
  const { agents } = useAgents();
  console.log("all agents", agents);

  return (
    <AgentChat
      agents={agents}
      agentId={agentId}
    />
  )
}
