// app/api/chat/route.ts
import { OpenAIStream, StreamingTextResponse } from 'ai'
import { Configuration, OpenAIApi } from 'openai-edge'
import { nanoid } from '@/lib/utils'

export const runtime = 'edge'

const configuration = new Configuration({
  apiKey: ""
})

const openai = new OpenAIApi(configuration)

export async function POST(req: Request) {
  const json = await req.json()
  const { messages, previewToken } = json

  if (!previewToken) {
    return new Response(
      JSON.stringify({ error: "API key missing" }),
      { status: 400 }
    );
  }

  let localOpenai;

  if (previewToken) {
    const localConfiguration = new Configuration({
      apiKey: previewToken
    });
    localOpenai = new OpenAIApi(localConfiguration);
  } else {
    localOpenai = openai;
  }

  const gptModel = 'gpt-3.5-turbo';

  const res = await localOpenai.createChatCompletion({
    model: gptModel,
    messages,
    temperature: 0.7,
    stream: true
  })

  console.log("Using API Key:", localOpenai?.configuration?.apiKey);
  console.log("Using GPT Model:", gptModel);

  const stream = OpenAIStream(res, {
    async onCompletion(completion) {
      const title = json.messages[0].content.substring(0, 100)
      const createdAt = Date.now()
      const id = json.id ?? nanoid();
      const path = `/chat/${id}`;
      const payload = {
        id,
        title,
        createdAt,
        path,
        messages: [
          ...messages,
          {
            content: completion,
            role: 'assistant'
          }
        ]
      }

      const saveTheChat = async () => {
        const baseUrl = process.env.BASE_URL || "http://localhost:3000";
        const res = await fetch(`${baseUrl}/api/saveChat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (res.ok) {
          console.log("Data saved");
        }
      };
      await saveTheChat();
 
    }
  })

  return new StreamingTextResponse(stream)
}
