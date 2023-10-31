// ui/app/api/bondai/stopAgent/route.ts

export async function POST(req: Request, res: Response) {
  try {
    const { agentId } = await req.json();
    console.log("api/bondai/stopAgent: Stop Agent: ", agentId);
    const agentResponse = await fetch(`http://backend:2663/agents/${agentId}/stop`, {
      cache: 'no-store',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    const parsedResponse = await agentResponse.json();
    console.error(`api/bondai/stopAgent response:`, parsedResponse);
    return Response.json(parsedResponse);

  } catch (error) {
    console.error('api/bondai/stopAgent error:', error);
    return new Response(JSON.stringify({error: "Failed to stop agent: " + error}), {
      status: 500,
    });
  }
}