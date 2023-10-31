// ui/lib/agentFileStorage.ts

interface MsgPayload {
  event: string;
  data: {
    agent_id: string | undefined;
    message: string;
  };
}

export const saveConversationToFile = (newMessage: MsgPayload) => {
  if (!newMessage)
    return null
  fetch('/api/bondai/saveAgentChat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newMessage),
  });
};

export const readConversationFromFile = async (agentId: string | undefined) => {
  if (!agentId)
    return null
  const conversationData = await fetch('/api/bondai/readAgentChat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ agentId: agentId }),
  });
  return conversationData;
};

export const removeConversationFromFile = async (agentId: string | undefined) => {
  if (!agentId)
    return null
  const conversationData = await fetch('/api/bondai/removeAgentChat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ agentId: agentId }),
  });
  return conversationData;
};