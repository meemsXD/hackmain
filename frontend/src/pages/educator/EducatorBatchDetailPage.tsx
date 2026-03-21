import { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { getBatch, getBatchQr, updateBatchStatus } from '@/api/batches';
import { getApiErrorMessage } from '@/api/client';
import { BatchTimeline, BlockedAttemptsTable, ChatPanel, QrCodeCard, SignatureConfirmModal, StatusBadge } from '@/components/shared';
import { Badge, Button, ErrorState, Loader } from '@/components/ui';
import { useAuth } from '@/auth/useAuth';
import { useBatchChat } from '@/features/chat/useBatchChat';
import { formatDateTime } from '@/utils/date';

export function EducatorBatchDetailPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { user, signatureToken } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [actionError, setActionError] = useState('');

  const batchQuery = useQuery({
    queryKey: ['batch', id, 'educator'],
    queryFn: () => getBatch(id),
  });

  const qrQuery = useQuery({
    queryKey: ['batch', id, 'qr'],
    queryFn: () => getBatchQr(id),
    enabled: Boolean(id),
  });

  const statusMutation = useMutation({
    mutationFn: (state: string) => updateBatchStatus(id, { state }),
    onSuccess: () => void batchQuery.refetch(),
  });

  const { messages, sendMessage } = useBatchChat(id, user?.full_name ?? 'Образователь', true);

  const latestStatus = useMemo(() => {
    const statuses = batchQuery.data?.statuses ?? [];
    return statuses[statuses.length - 1]?.state ?? 'CREATED';
  }, [batchQuery.data?.statuses]);

  if (batchQuery.isLoading) {
    return <Loader label="Загружаем карточку партии..." />;
  }

  if (batchQuery.isError || !batchQuery.data) {
    return <ErrorState description="Партия не найдена или недоступна." onRetry={() => void batchQuery.refetch()} />;
  }

  const batch = batchQuery.data;

  const cancelBatch = async (token: string) => {
    if (signatureToken && signatureToken !== token) {
      setActionError('Токен подписи не совпадает с сохраненным в профиле.');
      return;
    }
    setActionError('');
    try {
      await statusMutation.mutateAsync('CANCELLED');
    } catch (error) {
      setActionError(getApiErrorMessage(error));
    }
  };

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="page-title">Карточка партии #{batch.id}</h1>
            <p className="page-subtitle">Просмотр, отмена, QR и коммуникация с водителем.</p>
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
          <p>
            <span className="font-semibold">ID образователя:</span> {batch.medical_organization}
          </p>
          <p>
            <span className="font-semibold">ID переработчика:</span> {batch.delivery_point}
          </p>
          <p className="md:col-span-2">
            <span className="font-semibold">Адрес вывоза:</span> {batch.pickup_point}
          </p>
          <p>
            <span className="font-semibold">QR срок:</span> {formatDateTime(qrQuery.data?.time ?? batch.qr?.time ?? null)}
          </p>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Button variant="danger" onClick={() => setModalOpen(true)} disabled={latestStatus === 'CANCELLED'}>
            Отменить партию
          </Button>
          <Badge tone="warning">Редактирование партии в текущем backend API не предусмотрено</Badge>
        </div>
        {actionError ? <p className="mt-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{actionError}</p> : null}
      </article>

      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <div className="space-y-4">
          <BatchTimeline statuses={batch.statuses} />
          <ChatPanel messages={messages} onSend={sendMessage} />
        </div>
        <div className="space-y-4">
          <QrCodeCard qr={qrQuery.data ?? batch.qr} />
          <div className="surface p-4">
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-brand-700">Заблокированные попытки</h3>
            <BlockedAttemptsTable items={[]} />
          </div>
        </div>
      </div>

      <SignatureConfirmModal open={modalOpen} onClose={() => setModalOpen(false)} title="Подтвердить отмену партии" onConfirm={cancelBatch} />
    </section>
  );
}
