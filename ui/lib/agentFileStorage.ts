// ui/lib/agentFileStorage.ts

export const saveConversationToFile = (newMessage: string) => {
  fetch('/api/saveAgentChat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newMessage),
  });
};

export const readConversationFromFile = async (agentId: string) => {
  const conversationData = await fetch('/api/readAgentChat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ agentId: agentId }),
  });
  return conversationData;
};