import { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { extendBatchQr, getBatch, getBatchQr, listBatchQrLogs, updateBatchStatus } from '@/api/batches';
import { getApiErrorMessage } from '@/api/client';
import { BatchTimeline, BlockedAttemptsTable, ChatPanel, QrCodeCard, SignatureConfirmModal, StatusBadge } from '@/components/shared';
import { Badge, Button, ErrorState, Input, Loader } from '@/components/ui';
import { useAuth } from '@/auth/useAuth';
import { useBatchChat } from '@/features/chat/useBatchChat';
import { formatDateTime } from '@/utils/date';
import { getBatchLatestStatus, getQrExpiry } from '@/utils/batches';

export function EducatorBatchDetailPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { user, signatureToken } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [actionError, setActionError] = useState('');
  const [extendError, setExtendError] = useState('');
  const [extendHours, setExtendHours] = useState('24');

  const batchQuery = useQuery({
    queryKey: ['batch', id, 'educator'],
    queryFn: () => getBatch(id),
  });

  const qrQuery = useQuery({
    queryKey: ['batch', id, 'qr'],
    queryFn: () => getBatchQr(id),
    enabled: Boolean(id),
  });

  const logsQuery = useQuery({
    queryKey: ['batch', id, 'qr', 'logs'],
    queryFn: () => listBatchQrLogs(id, true),
    enabled: Boolean(id),
  });

  const statusMutation = useMutation({
    mutationFn: (state: string) => updateBatchStatus(id, { state }),
    onSuccess: () => void batchQuery.refetch(),
  });

  const extendMutation = useMutation({
    mutationFn: (hours: number) => extendBatchQr(id, hours),
    onSuccess: async () => {
      setExtendError('');
      await qrQuery.refetch();
      await logsQuery.refetch();
    },
  });

  const { messages, sendMessage } = useBatchChat(id, user?.full_name ?? 'Образователь', true);

  const latestStatus = useMemo(() => {
    if (!batchQuery.data) {
      return 'CREATED';
    }
    return getBatchLatestStatus(batchQuery.data);
  }, [batchQuery.data]);

  if (batchQuery.isLoading) {
    return <Loader label="Загружаем карточку партии..." />;
  }

  if (batchQuery.isError || !batchQuery.data) {
    return <ErrorState description="Партия не найдена или недоступна." onRetry={() => void batchQuery.refetch()} />;
  }

  const batch = batchQuery.data;
  const blockedAttempts = (logsQuery.data ?? []).map((item) => ({
    id: String(item.id),
    code: item.raw_code,
    reason: item.fail_reason || 'ACCESS_BLOCKED',
    createdAt: item.scanned_at,
  }));

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

  const handleExtendQr = async () => {
    const hours = Number(extendHours);
    if (!Number.isInteger(hours) || hours < 1 || hours > 168) {
      setExtendError('Укажите срок от 1 до 168 часов.');
      return;
    }

    try {
      setExtendError('');
      await extendMutation.mutateAsync(hours);
    } catch (error) {
      setExtendError(getApiErrorMessage(error));
    }
  };

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="page-title">Карточка партии #{batch.id}</h1>
            <p className="page-subtitle">Управление QR-доступом, статусом и коммуникацией с водителем.</p>
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
          {batch.created_by ? (
            <p>
              <span className="font-semibold">Создатель:</span> user:{batch.created_by}
            </p>
          ) : null}
          <p className="md:col-span-2">
            <span className="font-semibold">Адрес вывоза:</span> {batch.pickup_point}
          </p>
          <p>
            <span className="font-semibold">QR срок:</span> {formatDateTime(getQrExpiry(qrQuery.data ?? batch.qr))}
          </p>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Button variant="danger" onClick={() => setModalOpen(true)} disabled={latestStatus === 'CANCELLED'}>
            Отменить партию
          </Button>
          <Badge tone="warning">Редактирование полей партии в текущем API не предусмотрено</Badge>
        </div>
        {actionError ? <p className="mt-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{actionError}</p> : null}

        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
          <Input label="Продлить QR (часы, 1-168)" type="number" value={extendHours} onChange={(event) => setExtendHours(event.target.value)} />
          <Button variant="secondary" onClick={() => void handleExtendQr()} loading={extendMutation.isPending}>
            Продлить QR
          </Button>
        </div>
        {extendError ? <p className="mt-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{extendError}</p> : null}
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
            {logsQuery.isLoading ? <Loader label="Загружаем лог QR..." /> : null}
            {logsQuery.isError ? <p className="text-sm text-red-700">Не удалось загрузить лог QR.</p> : null}
            {!logsQuery.isLoading && !logsQuery.isError ? <BlockedAttemptsTable items={blockedAttempts} /> : null}
          </div>
        </div>
      </div>

      <SignatureConfirmModal open={modalOpen} onClose={() => setModalOpen(false)} title="Подтвердить отмену партии" onConfirm={cancelBatch} />
    </section>
  );
}
