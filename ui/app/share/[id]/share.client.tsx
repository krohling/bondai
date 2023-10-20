// app/share/[id]/share.client.tsx
"use client"
import { useState, useEffect } from 'react'
import { type Metadata } from 'next'
import { formatDate } from '@/lib/utils'
import { getSharedChat } from '@/app/actions'
import { ChatList } from '@/components/chat-list'
import { FooterText } from '@/components/footer'
import { type Chat } from '@/lib/types'

export interface SharePageProps {
  params: {
    id: string
  }
}

export async function generateMetadata({
  params
}: SharePageProps): Promise<Metadata> {
  const chat = await getSharedChat(params.id)

  return {
    title: chat?.title.slice(0, 50) ?? 'Chat'
  }
}

export default function SharePageClient({ params }: SharePageProps) {
  const [chat, setChat] = useState<Chat | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const fetchedChat = await getSharedChat(params.id);
      if (!fetchedChat || !fetchedChat.path) {
        window.location.href = "/404";
      } else {
        setChat(fetchedChat);
      }
    };
    
    fetchData();
  }, [params.id]);

  if (!chat) {
    return <div className="p-5">Loading...</div>;
  }

  return (
    <>
      <div className="flex-1 space-y-6">
        <div className="px-4 py-6 border-b bg-background md:px-6 md:py-8">
          <div className="max-w-2xl mx-auto md:px-6">
            <div className="space-y-1 md:-mx-8">
              <h1 className="text-2xl font-bold">{chat.title}</h1>
              <div className="text-sm text-muted-foreground">
                {formatDate(chat.createdAt)} · {chat.messages.length} messages
              </div>
            </div>
          </div>
        </div>
        <ChatList messages={chat.messages} />
      </div>
      <FooterText className="py-8" />
    </>
  )
}