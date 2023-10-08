// app/api/clearChats/route.ts
import { clearChats } from "@/app/actions";

export async function POST(req: Request, res: Response) {
  try {
    await clearChats();
    return Response.json({ message: "Chats cleared" });
  } catch (error) {
    return new Response('Failed to clear chat', {
      status: 500,
    })
  }
};
