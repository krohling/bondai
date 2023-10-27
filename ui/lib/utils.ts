// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { customAlphabet } from 'nanoid'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const nanoid = customAlphabet(
  '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
  7
) // 7-character random string

export const getAgentName = (agent_id: string) => {
  let agentName = localStorage.getItem('bondai_agent_' + agent_id);
  if (agentName) {
    return agentName;
  } else {
    // Retrieve existing IDs
    const existingIDs = JSON.parse(localStorage.getItem("existing_agent_ids") || "[]");

    // Generate a new unique ID
    let newID;
    do {
      newID = Math.floor(Math.random() * 100);
    } while (existingIDs.includes(newID));

    // Add the new ID to the list and update localStorage
    existingIDs.push(newID);
    localStorage.setItem("existing_agent_ids", JSON.stringify(existingIDs));

    // Create the new agent name
    agentName = 'Agent ' + newID;
    localStorage.setItem('bondai_agent_' + agent_id, agentName);
    return agentName;
  }
};

export async function fetcher<JSON = any>(
  input: RequestInfo,
  init?: RequestInit
): Promise<JSON> {
  const res = await fetch(input, init)

  if (!res.ok) {
    const json = await res.json()
    if (json.error) {
      const error = new Error(json.error) as Error & {
        status: number
      }
      error.status = res.status
      throw error
    } else {
      throw new Error('An unexpected error occurred')
    }
  }

  return res.json()
}

export function formatDate(input: string | number | Date): string {
  const date = new Date(input)
  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

export function isJSON(str: string) {
  try {
      JSON.parse(str);
  } catch (e) {
      return false;
  }
  return true;
}

export const convertObjectToString = (obj: any): string => {
  let str = '';
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'object' && value !== null) {
      str += `${key.charAt(0).toUpperCase() + key.slice(1)}: \n${convertObjectToString(value)}\n`;
    } else {
      str += `${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}\n`;
    }
  }
  return str.trim();
};