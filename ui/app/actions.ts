// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { hmset, zadd, hgetall, zrange, del, zrem } from '@/lib/fileStorage';
import { type Chat } from '@/lib/types'

type ChatScore = {
  score: number;
  member: string;
};

export async function getChats(userId?: string | null) {
  if (!userId) {
    return []
  }
  try {
    const chats: ChatScore[] = await zrange(`user:chat:${userId}`, 0, -1, { rev: true });
    const results = [];
    for (const chat of chats) {
      const chatData = await hgetall(chat.member);
      results.push(chatData);
    }
    return results as Chat[];
  } catch (error) {
    return []
  }
}

export async function getChat(id: string, userId: string) {
  const chat = await hgetall<Chat>(`chat:${id}`);
  if (!chat || (userId && chat.userId !== userId)) {
    return null;
  }
  return chat;
}

export async function removeChat({ id, path }: { id: string; path: string }) {
  const uid = await hgetall<string>(`chat:${id}`);
  await del(`chat:${id}`);
  await zrem(`user:chat:${uid}`, `chat:${id}`);
  revalidatePath('/');
  return revalidatePath(path);
}

export async function clearChats() {
  try {
    const chats = await zrange(`user:chat:ABC123`, 0, -1) as ChatScore[];
    if (!chats.length) {
      console.log("clearChats: No chats to clear. Redirecting...");
      return "error";
    }
    await Promise.all(chats.map(chat => clearSingleChat(chat)));
    revalidatePath('/');
    return revalidatePath('/');
  } catch (error) {
    console.error("clearChats: An error occurred", error);
  }
}

async function clearSingleChat(chat: ChatScore) {
  try {
    await del(chat.member);
    await zrem(`user:chat:ABC123`, chat.member);
  } catch (error) {
    console.error("clearSingleChat: An error occurred while clearing a single chat", error);
  }
}

export async function getSharedChat(id: string) {
  const chat = await hgetall<Chat>(`chat:${id}`);
  if (!chat || !chat.path) {
    return null;
  }
  return chat;
}

export async function shareChat(chat: Chat) {
  const payload = {
    ...chat.chat,
    sharePath: `/share/${chat.chat.id}`
  };
  await hmset(`chat:${chat.chat.id}`, payload);
  return payload;
}

export async function saveChat(payload: any) {
  const id = payload.id;
  const createdAt = payload.createdAt;
  await hmset(`chat:${id}`, payload);
  await zadd(`user:chat:ABC123`, {
    score: createdAt,
    member: `chat:${id}`
  });
  return payload;
}
