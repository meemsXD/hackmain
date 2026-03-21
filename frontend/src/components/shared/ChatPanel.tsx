import { useState } from 'react';
import type { ChatMessage } from '@/api/types';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';
import { formatDateTime } from '@/utils/date';

type ChatPanelProps = {
  title?: string;
  messages: ChatMessage[];
  loading?: boolean;
  canSend?: boolean;
  onSend?: (body: string) => Promise<void> | void;
};

export function ChatPanel({ title = 'Чат по партии', messages, loading = false, canSend = true, onSend }: ChatPanelProps) {
  const [body, setBody] = useState('');

  const handleSend = async () => {
    if (!body.trim() || !onSend) {
      return;
    }
    await onSend(body.trim());
    setBody('');
  };

  return (
    <div className="surface p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-brand-700">{title}</h3>
      <div className="max-h-64 space-y-2 overflow-y-auto rounded-xl border border-brand-100 bg-brand-50/60 p-3">
        {loading ? <p className="text-sm text-brand-600">Загружаем сообщения...</p> : null}
        {!loading && !messages.length ? <p className="text-sm text-brand-600">Чат пуст.</p> : null}
        {messages.map((message) => (
          <article
            key={message.id}
            className={`rounded-lg px-3 py-2 text-sm ${message.isSystem ? 'bg-amber-50 text-amber-900' : 'bg-white text-brand-900'}`}
          >
            <p className="font-medium">{message.isSystem ? 'Система' : message.authorName}</p>
            <p className="mt-1 whitespace-pre-wrap">{message.body}</p>
            <p className="mt-1 text-xs opacity-70">{formatDateTime(message.createdAt)}</p>
          </article>
        ))}
      </div>
      {canSend ? (
        <div className="mt-3 space-y-2">
          <Textarea value={body} onChange={(event) => setBody(event.target.value)} placeholder="Введите сообщение..." />
          <Button onClick={handleSend} disabled={!body.trim()}>
            Отправить
          </Button>
        </div>
      ) : (
        <p className="mt-3 text-sm text-brand-700">Для вашей роли чат доступен только в режиме чтения.</p>
      )}
    </div>
  );
}
