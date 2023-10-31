// ui/app/api/readAgentChat/route.ts
import fs from 'fs';
import path from 'path';
const DATA_DIR = path.resolve(process.cwd(), 'data');

export async function POST(req: Request, res: Response) {
  try {
    const { agentId } = await req.json();
    console.log("agentId", agentId);
    const filePath = path.join(DATA_DIR, `${agentId}.json`);
    console.log("filePath", filePath);
    
    if (fs.existsSync(filePath)) {
      const convString = fs.readFileSync(filePath, 'utf8');
      const wrappedConvString = `{"messages":${convString}}`;
      return new Response(wrappedConvString);
    } else {
      return new Response('{}');
    }
    
  } catch (error) {
    console.log('Sending 500 response: Failed to read chat', error);
    return new Response('Failed to read chat ' + error, {
      status: 500,
    })
  }
};