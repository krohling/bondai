// ui/lib/agentActions.ts

export const startAgentAPI = async (agentId: string | undefined, budgetValue: string, maxStepsValue: string) => {
  try {
    if (!agentId) {
      console.log('startAgentServer: agentId not found:', agentId);
      return null 
    }
    const res = await fetch(`/api/bondai/startAgent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        agentId: agentId,
        task: "",
        task_budget: budgetValue,
        max_steps: maxStepsValue,
      }),
    });
    const startAgent = await res.json();
    console.log('startAgent:', startAgent, 'agentId:', agentId);
    if (startAgent.status == "success") {
      // Success status informs us the start up request was received
      // component re-render will occur on receipt of conversational_agent_message websocket event
    }
    return;

  } catch (error: any) {
    console.log('Cannot start agent:', error.message);
  }
};

export const stopAgentAPI = async (agentId: string | undefined) => {
  try {
    if (!agentId) {
      console.log('stopAgentServer: agentId not found:', agentId);
      return null 
    }
    const res = await fetch(`/api/bondai/stopAgent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        agentId: agentId,
      }),
    });
    const stopAgent = await res.json();
    console.log('stopAgent:', stopAgent, 'agentId:', agentId);
    return stopAgent;

  } catch (error) {
    console.log('Cannot stop agent:', error);
  }
};
  