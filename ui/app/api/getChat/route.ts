// api/getChat/route.ts
import { getChat } from "@/app/actions";

export async function POST(req: Request, res: Response) {
  try {
    const { id, userId } = await req.json();
    const chat = await getChat(id, userId);
    if (chat) {
      return Response.json(chat);
    } else {
      return new Response('Chat not found', {
        status: 404,
      })
    }
  } catch (error) {
    return new Response('Failed to fetch chat', {
      status: 500,
    })
  }
};
