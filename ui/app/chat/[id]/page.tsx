// app/chat/[id]/page.tsx
"use client"
import ChatPageClient from './chat.client'

export interface ChatPageProps {
  params: {
    id: string;
  };
}

export default function ChatPage({ params }: ChatPageProps) { 
  return (
    <>     
      <ChatPageClient params={params}/>
    </>
  )
}