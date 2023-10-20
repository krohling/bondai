// api/removeChat/route.ts
import { removeChat } from "@/app/actions";

export async function POST(req: Request, res: Response) {
  const { id, path } = await req.json();

  try {
    await removeChat({ id, path });
    return Response.json({ message: "Chat removed" });
  } catch (error) {
    return new Response('Failed to clear chat', {
      status: 500,
    })
  }
};
