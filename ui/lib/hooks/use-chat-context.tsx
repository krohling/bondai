// lib/hooks/use-chat-context.ts
'use client'
import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useEffect } from 'react';
import { Chat } from '@/lib/types';

interface ChatContextProps {
  chats: Chat[] | null;
  setChats: React.Dispatch<React.SetStateAction<Chat[] | null>>;
  clearChats: () => void;
}

const ChatContext = createContext<ChatContextProps | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
  initialChats?: any[];
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children, initialChats }) => {
  const [chats, setChats] = useState<Chat[] | null>(initialChats || null);

  useEffect(() => {
    const fetchChats = async () => {
      const userId = "ABC123";
      const res = await fetch(`${window.location.origin}/api/getChats`, {
        method: 'POST',
        cache: 'no-store',
        body: JSON.stringify({ userId }),
      });

      if (res.ok) {
        const data = await res.json();
        setChats(data);
      }
    };

    fetchChats();
  }, []);

  const clearChats = () => {
    setChats([]);
  };

  return (
    <ChatContext.Provider value={{ chats, setChats, clearChats }}>
      {children}
    </ChatContext.Provider>
  );
};
