// components/sidebar-list.tsx
'use client';
import React, { useEffect, useState } from 'react';
import { SidebarActions } from '@/components/sidebar-actions';
import { SidebarItem } from '@/components/sidebar-item';
import { Chat } from '@/lib/types';
import { useChatContext } from '@/lib/hooks/use-chat-context';

export interface SidebarListProps {
  userId?: string;
  chats: Chat[];
  setChats: React.Dispatch<React.SetStateAction<Chat[]>>;
}

export function SidebarList({ userId }: SidebarListProps) {
  const { chats, setChats } = useChatContext(); 

  const handleRemoveChat = async ({ id, path }: { id: string; path: string }): Promise<void> => {
    const res = await fetch(`${window.location.origin}/api/removeChat`, {
      method: 'POST',
      body: JSON.stringify({ id, path }),
    });
    
    if (res.ok) {
      setChats(chats?.filter(chat => chat.id !== id) || null);
    }
  };

  const handleShareChat = async (chat: Chat): Promise<Chat | { error: string }> => {
    try {
      const res = await fetch(`${window.location.origin}/api/shareChat`, {
        method: 'POST',
        body: JSON.stringify({ chat }),
      });
  
      if (res.ok) {
        const data = await res.json();
        return data;
      } else {
        return { error: 'Failed to share chat' };
      }
    } catch (error: any) {
      return { error: error.message };
    }
  };

  useEffect(() => {
    const refreshChatList = async () => {

      try {
        const res = await fetch(`${window.location.origin}/api/getChats`, {
          method: 'POST',
          cache: 'no-store',
          body: JSON.stringify({ userId }),
        });
        if (res.ok) {
          const data = await res.json();
          setChats(data);
        }
      } catch (error) {
        console.error('refreshChatList: Failed to fetch chats:', error);
      }
    };
    
    refreshChatList();
  }, []);

  return (
    <div className="flex-1 overflow-auto">
      {chats?.length ? (
        <>
        <div className="space-y-2 px-2">
          {chats.map(
            (chat) =>
              chat && (
                <SidebarItem key={chat?.id} chat={chat}>
                <SidebarActions 
                  chat={chat} 
                  removeChat={handleRemoveChat} 
                  shareChat={handleShareChat} 
                />
                </SidebarItem>
              )
          )}
        </div>
        </>
      ) : (
        <div className="p-8 text-center">
          <p className="text-sm text-muted-foreground">No chat history</p>
        </div>
      )}
    </div>
  );
}
