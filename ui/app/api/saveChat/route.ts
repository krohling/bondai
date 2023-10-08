// app/api/saveChat/route.ts
import { saveChat } from "@/app/actions";

export async function POST(req: Request, res: Response) {
  try {
    const chat = await req.json();
    
    if (!chat) {
      console.log('Sending 400 response: Chat data is missing');
      return new Response('Chat data is missing', {
        status: 400,
      })
    }

    const savedChat = await saveChat(chat);
    return Response.json(savedChat);

  } catch (error) {
    console.log('Sending 500 response: Failed to save chat', error);
    return new Response('Failed to save chat', {
      status: 500,
    })
  }
};
