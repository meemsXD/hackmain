import { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { getBatch, updateBatchStatus } from '@/api/batches';
import { getApiErrorMessage } from '@/api/client';
import { useAuth } from '@/auth/useAuth';
import { BatchTimeline, ChatPanel, SignatureConfirmModal, StatusBadge } from '@/components/shared';
import { Badge, Button, ErrorState, Loader } from '@/components/ui';
import { useBatchChat } from '@/features/chat/useBatchChat';
import { formatDateTime, isExpired } from '@/utils/date';
import { getBatchLatestStatus, getQrExpiry } from '@/utils/batches';

type PendingAction = 'pickup' | 'delivered' | null;

export function DriverBatchDetailPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { user, signatureToken } = useAuth();
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [actionError, setActionError] = useState('');

  const batchQuery = useQuery({
    queryKey: ['batch', id, 'driver'],
    queryFn: () => getBatch(id),
  });

  const statusMutation = useMutation({
    mutationFn: (state: string) => updateBatchStatus(id, { state }),
    onSuccess: () => void batchQuery.refetch(),
  });

  const { messages, sendMessage } = useBatchChat(id, user?.full_name ?? 'Водитель', true);

  const batch = batchQuery.data;
  const latestStatus = useMemo(() => {
    if (!batch) {
      return 'CREATED';
    }
    return getBatchLatestStatus(batch);
  }, [batch]);

  const tokenExpired = isExpired(getQrExpiry(batch?.qr)) || !batch?.qr?.is_active;
  const canPickup = latestStatus === 'CREATED' && !tokenExpired;
  const canDelivered = ['IN_TRANSIT', 'DELIVERED'].includes(latestStatus) && !tokenExpired;

  if (batchQuery.isLoading) {
    return <Loader label="Загружаем карточку..." />;
  }

  if (batchQuery.isError || !batch) {
    return <ErrorState description="Не удалось загрузить партию." onRetry={() => void batchQuery.refetch()} />;
  }

  const executeAction = async (token: string) => {
    if (signatureToken && signatureToken !== token) {
      setActionError('Токен подписи не совпадает с токеном в вашем профиле.');
      return;
    }

    const nextStatus = pendingAction === 'pickup' ? 'IN_TRANSIT' : 'DELIVERED';

    try {
      setActionError('');
      await statusMutation.mutateAsync(nextStatus);
    } catch (error) {
      setActionError(getApiErrorMessage(error));
    } finally {
      setPendingAction(null);
    }
  };

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="page-title">Карточка водителя: партия #{batch.id}</h1>
            <p className="page-subtitle">Подтверждение забора и отметка о доставке на переработку.</p>
          </div>
          <StatusBadge status={latestStatus} />
        </div>

        <div className="mt-4 grid gap-2 text-sm text-brand-900 md:grid-cols-2">
          <p>
            <span className="font-semibold">Тип отходов:</span> {batch.waste_type}
          </p>
          <p>
            <span className="font-semibold">Количество:</span> {batch.quantity}
          </p>
          {batch.created_by ? (
            <p>
              <span className="font-semibold">Создатель:</span> user:{batch.created_by}
            </p>
          ) : null}
          <p className="md:col-span-2">
            <span className="font-semibold">Адрес вывоза:</span> {batch.pickup_point}
          </p>
          <p>
            <span className="font-semibold">Срок доступа:</span> {formatDateTime(getQrExpiry(batch.qr))}
          </p>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Button disabled={!canPickup} onClick={() => setPendingAction('pickup')}>
            Подтвердить забор
          </Button>
          <Button variant="secondary" disabled={!canDelivered} onClick={() => setPendingAction('delivered')}>
            Отметить доставку
          </Button>
          {tokenExpired ? <Badge tone="danger">Срок действия QR истек: действия заблокированы</Badge> : null}
        </div>
        {actionError ? <p className="mt-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{actionError}</p> : null}
      </article>

      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <div className="space-y-4">
          <BatchTimeline statuses={batch.statuses} />
          <ChatPanel messages={messages} onSend={sendMessage} />
        </div>
        <aside className="surface p-4">
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-700">Подсказка</h3>
          <p className="text-sm text-brand-800">
            Критичные действия подтверждаются токеном подписи. Токен создается автоматически и доступен в вашем профиле.
          </p>
        </aside>
      </div>

      <SignatureConfirmModal
        open={pendingAction !== null}
        onClose={() => setPendingAction(null)}
        title={pendingAction === 'pickup' ? 'Подтвердить забор' : 'Подтвердить доставку'}
        onConfirm={executeAction}
      />
    </section>
  );
}
