// components/chat-layout.tsx
'use client';
import { ChatProvider } from '@/lib/hooks/use-chat-context';

export default function ChatLayout({ children }: { children: React.ReactNode }) {

  return (
    <ChatProvider>
      {children}
    </ChatProvider>
  );
}