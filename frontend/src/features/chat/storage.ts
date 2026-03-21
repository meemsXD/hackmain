import type { ChatMessage } from '@/api/types';

const KEY = 'waste_mvp_chat_messages';

type ChatBucket = Record<string, ChatMessage[]>;

function read(): ChatBucket {
  if (typeof window === 'undefined') {
    return {};
  }
  const raw = localStorage.getItem(KEY);
  if (!raw) {
    return {};
  }
  try {
    return JSON.parse(raw) as ChatBucket;
  } catch {
    return {};
  }
}

function write(payload: ChatBucket) {
  if (typeof window === 'undefined') {
    return;
  }
  localStorage.setItem(KEY, JSON.stringify(payload));
}

export function loadMessages(batchId: string): ChatMessage[] {
  return read()[batchId] ?? [];
}

export function sendMessage(batchId: string, message: Omit<ChatMessage, 'id' | 'createdAt'>): ChatMessage {
  const next: ChatMessage = {
    id: crypto.randomUUID(),
    createdAt: new Date().toISOString(),
    ...message,
  };
  const bucket = read();
  const current = bucket[batchId] ?? [];
  bucket[batchId] = [...current, next];
  write(bucket);
  return next;
}
