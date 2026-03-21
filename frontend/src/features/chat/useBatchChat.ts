import { useCallback, useEffect, useState } from 'react';
import type { ChatMessage } from '@/api/types';
import { loadMessages, sendMessage as sendChatMessage } from '@/features/chat/storage';

export function useBatchChat(batchId: string, authorName: string, canSend = true) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const reload = useCallback(() => {
    setMessages(loadMessages(batchId));
  }, [batchId]);

  useEffect(() => {
    reload();
    const timer = window.setInterval(reload, 10_000);
    return () => window.clearInterval(timer);
  }, [reload]);

  const sendMessage = useCallback(
    async (body: string) => {
      if (!canSend) {
        return;
      }
      sendChatMessage(batchId, {
        authorId: null,
        authorName,
        body,
        isSystem: false,
      });
      reload();
    },
    [authorName, batchId, canSend, reload],
  );

  return { messages, sendMessage, reload };
}
