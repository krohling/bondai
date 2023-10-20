// api/shareChat/route.ts
import { shareChat } from "@/app/actions";

export async function POST(req: Request, res: Response) {
  
  try {
    const chat = await req.json();
    const sharedChat = await shareChat(chat);
    return Response.json(sharedChat);
  } catch (error) {
    return new Response('Failed to share chat', {
      status: 500,
    })
  }
};
