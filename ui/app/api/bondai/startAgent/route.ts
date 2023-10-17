// app/api/bondai/startAgent/route.ts

export async function GET(req: Request, res: Response) {
  try {
    console.log("api/bondai/startAgent: Start");
    const agentResponse = await fetch('http://backend:2663/agent/start', {
      cache: 'no-store',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task: 'write the word test and save it to file. no budget and no other criteria. please proceed. accept this as confirmation to go ahead without asking permission again.',
        task_budget: 1.00,
        max_steps: 10,
      }),
    });
    const parsedResponse = await agentResponse.json();
    console.error(`api/bondai/startAgent response: ${agentResponse.statusText}`, parsedResponse.state);
    return Response.json(parsedResponse);

  } catch (error) {
    console.error('api/bondai/startAgent error:', error);
    return new Response('Failed to start agent', {
      status: 500,
    });
  }
}
