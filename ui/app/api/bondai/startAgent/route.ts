// app/api/bondai/startAgent/route.ts

export async function POST(req: Request, res: Response) {
  try {
    const { agentId } = await req.json();
    console.log("api/bondai/startAgent: Start Agent: ", agentId);
    const agentResponse = await fetch(`http://backend:2663/agents/${agentId}/start`, {
      cache: 'no-store',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task: "",
        /*task_budget: budgetValue,*/
        /*max_steps: maxStepsValue,*/
      }),
    });
    const parsedResponse = await agentResponse.json();
    console.error(`api/bondai/startAgent response:`, parsedResponse);
    return Response.json(parsedResponse);

  } catch (error) {
    console.error('api/bondai/startAgent error:', error);
    return new Response('Failed to start agent', {
      status: 500,
    });
  }
}
