// app/api/bondai/getAgentStatus/route.ts

export async function GET(req: Request, res: Response) {
  try {
    console.log("api/bondai/startAgent: Start");
    const agentResponse = await fetch('http://backend:2663/agent', { cache: 'no-store' });

    const parsedResponse = await agentResponse.json();
    console.error(`api/bondai/getAgentStatus response: ${agentResponse.statusText}`, parsedResponse.state);
    parsedResponse.httpStatus = agentResponse.status;
    return Response.json(parsedResponse);
    
  } catch (error) {
    console.error('api/bondai/startAgent error:', error);
    return new Response('Failed to start agent', {
      status: 500,
    });
  }
}