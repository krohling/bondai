// lib/fileStorage.ts
import fs from 'fs';
const path = require('path');
const DATA_DIR = path.resolve(process.cwd(), 'data');

export const hmset = async <T>(key: string, payload: T) => {
  try {
    const filePath = `${DATA_DIR}/${key}.json`;
    fs.writeFileSync(filePath, JSON.stringify(payload, null, 2));
  } catch (error) {
    console.log("error zadd", error);
  }
}

export const zadd = async (key: string, { score, member }: { score: number; member: string }) => {
  try {
    const filePath = `${DATA_DIR}/${key}.json`;
    let data: { score: number; member: string }[] = [];
    
    if (fs.existsSync(filePath)) {
      const rawData = fs.readFileSync(filePath, 'utf-8');
      data = JSON.parse(rawData);
    }
    
    const existingEntryIndex = data.findIndex((entry) => entry.member === member);

    if (existingEntryIndex !== -1) {
      data[existingEntryIndex].score = score;
    } else {
      data.push({ score, member });
    }
    
    data.sort((a, b) => a.score - b.score);

    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  } catch (error) {
    console.log("zadd: error", error);
  }
}

export const hgetall = async <T>(key: string): Promise<T | null> => {
  const filePath = `${DATA_DIR}/${key}.json`;
  if (fs.existsSync(filePath)) {
    const rawData = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(rawData) as T;
  }
  return null;
}

export const zrange = async <T>(key: string, start: number, end: number, options?: { rev?: boolean }): Promise<T[]> => {
  
  const filePath = `${DATA_DIR}/${key}.json`;
  if (fs.existsSync(filePath)) {
    const rawData = fs.readFileSync(filePath, 'utf-8');
    let data: T[] = JSON.parse(rawData);

    if (options?.rev) {
      data.reverse();
    }

    if (end === -1) {
      return data.slice(start);  // this will slice from 'start' to the end of the array
    }

    return data.slice(start, end + 1);
  }
  return [];
}

export const del = async (key: string) => {
  const filePath = `${DATA_DIR}/${key}.json`;
  try {
    fs.unlink(filePath, (err) => {
      if (err) throw err;
    });
  } catch (error) {
    console.error(`del: An error occurred while deleting the file ${filePath}`, error);
  }
}

export const zrem = async (key: string, member: string) => {
  const filePath = `${DATA_DIR}/${key}.json`;
  if (fs.existsSync(filePath)) {
    const rawData = fs.readFileSync(filePath, 'utf-8');
    let data = JSON.parse(rawData);

    const updatedData = data.filter((item: { member: string }) => item.member !== member);

    fs.writeFileSync(filePath, JSON.stringify(updatedData));
  }
}
