// app/chat/[id]/chat.client.tsx
"use client"
import { useState, useEffect } from 'react'
import { Chat } from '@/components/chat'
import { notFound } from 'next/navigation'

export interface ChatPageProps {
  params: {
    id: string;
  };
}

const ChatPageClient = ({ params }: ChatPageProps) => {

  interface ChatType {
    id: string;
    userId: string;
    messages: any[];
  }

  const [chat, setChat] = useState<ChatType | null>(null);

  useEffect(() => {
    const fetchChat = async () => {
      const res = await fetch(`/api/getChat`, {
        method: 'POST',
        body: JSON.stringify({ id: params.id })  
      })
      if (res.ok) {
        setChat(await res.json()) 
      } else {
        notFound()
      }
    }
    fetchChat()
  }, [params.id])

  if (!chat) {
    return <p className="p-5">Loading...</p> 
  }

  return (
    <Chat 
      id={chat.id}
      initialMessages={chat.messages ?? []} 
    />
  )

}

export default ChatPageClient