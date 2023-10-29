// ui/app/api/saveAgentChat/route.ts
import fs from 'fs';
import path from 'path';
const DATA_DIR = path.resolve(process.cwd(), 'data');

export async function POST(req: Request, res: Response) {
  try {
    const conversationData = await req.json();
    const agentId = conversationData.data.agent_id;
    const filePath = path.join(DATA_DIR, `${agentId}.json`);

    let existingConversation = [];

    if (fs.existsSync(filePath)) {
      const jsonString = fs.readFileSync(filePath, 'utf8');
      existingConversation = JSON.parse(jsonString);
    }

    existingConversation.push(conversationData);

    const jsonString = JSON.stringify(existingConversation, null, 2);
    fs.writeFileSync(filePath, jsonString);

    return Response.json({ message: 'Conversation saved.' });

  } catch (error) {
    console.log('Sending 500 response: Failed to save chat', error);
    return new Response('Failed to save chat ' + error, {
      status: 500,
    })
  }
};
