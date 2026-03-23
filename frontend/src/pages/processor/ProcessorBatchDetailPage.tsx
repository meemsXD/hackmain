import { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { getBatch, updateBatchStatus } from '@/api/batches';
import { getApiErrorMessage } from '@/api/client';
import { useAuth } from '@/auth/useAuth';
import { BatchTimeline, ChatPanel, SignatureConfirmModal, StatusBadge } from '@/components/shared';
import { Badge, Button, ErrorState, Loader } from '@/components/ui';
import { useBatchChat } from '@/features/chat/useBatchChat';
import { formatDateTime } from '@/utils/date';
import { getBatchLatestStatus, getQrExpiry } from '@/utils/batches';

export function ProcessorBatchDetailPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { user, signatureToken } = useAuth();
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [actionError, setActionError] = useState('');

  const batchQuery = useQuery({
    queryKey: ['batch', id, 'processor'],
    queryFn: () => getBatch(id),
  });

  const acceptMutation = useMutation({
    mutationFn: () => updateBatchStatus(id, { state: 'ACCEPTED' }),
    onSuccess: () => void batchQuery.refetch(),
  });

  const { messages } = useBatchChat(id, user?.full_name ?? 'Переработчик', false);

  const latestStatus = useMemo(() => {
    if (!batchQuery.data) {
      return 'CREATED';
    }
    return getBatchLatestStatus(batchQuery.data);
  }, [batchQuery.data]);

  if (batchQuery.isLoading) {
    return <Loader label="Загружаем партию..." />;
  }

  if (batchQuery.isError || !batchQuery.data) {
    return <ErrorState description="Не удалось загрузить карточку партии." onRetry={() => void batchQuery.refetch()} />;
  }

  const batch = batchQuery.data;
  const canAccept = latestStatus !== 'ACCEPTED' && latestStatus !== 'CANCELLED';

  const confirmAccept = async (token: string) => {
    if (signatureToken && signatureToken !== token) {
      setActionError('Токен подписи не совпадает.');
      return;
    }
    setActionError('');
    try {
      await acceptMutation.mutateAsync();
      setConfirmOpen(false);
    } catch (error) {
      setActionError(getApiErrorMessage(error));
    }
  };

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="page-title">Приемка партии #{batch.id}</h1>
            <p className="page-subtitle">Финальное подтверждение получения отходов переработчиком.</p>
          </div>
          <StatusBadge status={latestStatus} />
        </div>
        <div className="mt-4 grid gap-2 text-sm text-brand-900 md:grid-cols-2">
          <p>
            <span className="font-semibold">Тип:</span> {batch.waste_type}
          </p>
          <p>
            <span className="font-semibold">Количество:</span> {batch.quantity}
          </p>
          {batch.created_by ? (
            <p>
              <span className="font-semibold">Создатель:</span> user:{batch.created_by}
            </p>
          ) : null}
          <p>
            <span className="font-semibold">Адрес вывоза:</span> {batch.pickup_point}
          </p>
          <p>
            <span className="font-semibold">QR срок:</span> {formatDateTime(getQrExpiry(batch.qr))}
          </p>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Button onClick={() => setConfirmOpen(true)} disabled={!canAccept || acceptMutation.isPending}>
            Подтвердить приемку
          </Button>
          <Badge tone="warning">Чат переработчика в MVP доступен только для чтения</Badge>
        </div>
        {actionError ? <p className="mt-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{actionError}</p> : null}
      </article>

      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <BatchTimeline statuses={batch.statuses} />
        <ChatPanel messages={messages} canSend={false} />
      </div>

      <SignatureConfirmModal open={confirmOpen} onClose={() => setConfirmOpen(false)} title="Подтвердить приемку" onConfirm={confirmAccept} />
    </section>
  );
}
