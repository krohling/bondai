// api/getChats/route.ts
import { getChats } from "@/app/actions";

export async function POST(req: Request, res: Response) {
  try {
    const { userId } = await req.json();

    if (!userId) {
      console.log('Sending 400 response: userId is missing');
      return new Response('userId is missing', {
        status: 400,
      })
    }

    const chats = await getChats(userId);
    return Response.json(chats);
  } catch (error) {
    return new Response('Failed to fetch chats', {
      status: 500,
    })
  }
};
