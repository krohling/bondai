// ui/app/api/saveAgentChat/route.ts
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
const DATA_DIR = path.resolve(process.cwd(), 'data');

function generateHash(payload: any) {
  const hash = crypto.createHash('sha256');
  hash.update(JSON.stringify(payload));
  return hash.digest('hex');
}

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

    const newMessageId = generateHash(conversationData);

    let isDuplicate = false;
    if (conversationData.data.event != 'conversational_agent_started' &&
        conversationData.data.event != 'task_agent_completed') {
      isDuplicate = existingConversation.some(
        (conv: { messageId: string; }) => conv.messageId === newMessageId
      );
    }

    if (!isDuplicate) {
      existingConversation.push({ messageId: newMessageId, ...conversationData });
      const jsonString = JSON.stringify(existingConversation, null, 2);
      fs.writeFileSync(filePath, jsonString);
      return Response.json({ message: 'Conversation saved.' });
    } else {
      console.log('Duplicate message, not saving.');
      return Response.json({ message: 'Duplicate message, not saving.' });
    }

  } catch (error) {
    console.log('Sending 500 response: Failed to save chat', error);
    return new Response('Failed to save chat ' + error, {
      status: 500,
    })
  }
};

