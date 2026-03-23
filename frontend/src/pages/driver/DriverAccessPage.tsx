import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { scanQrCode } from '@/api/batches';
import { getApiErrorMessage } from '@/api/client';
import type { BatchQr, WasteBatch } from '@/api/types';
import { formatDateTime } from '@/utils/date';
import { getBatchLatestStatus, getQrExpiry } from '@/utils/batches';
import { StatusBadge } from '@/components/shared';
import { Button, ErrorState, Input } from '@/components/ui';

export function DriverAccessPage() {
  const [searchParams] = useSearchParams();
  const codeFromUrl = searchParams.get('code')?.trim() ?? '';

  const [code, setCode] = useState('');
  const [foundBatch, setFoundBatch] = useState<WasteBatch | null>(null);
  const [scannedQr, setScannedQr] = useState<BatchQr | null>(null);
  const [error, setError] = useState('');
  const [autoChecked, setAutoChecked] = useState(false);

  const checkMutation = useMutation({
    mutationFn: (value: string) => scanQrCode({ code: value }),
    onSuccess: (response) => {
      setError('');
      setFoundBatch(response.batch);
      setScannedQr(response.qr);
    },
    onError: (requestError) => {
      setError(getApiErrorMessage(requestError));
      setFoundBatch(null);
      setScannedQr(null);
    },
  });

  useEffect(() => {
    if (!autoChecked && codeFromUrl) {
      setCode(codeFromUrl);
      checkMutation.mutate(codeFromUrl);
      setAutoChecked(true);
    }
  }, [autoChecked, checkMutation, codeFromUrl]);

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Доступ по QR-коду</h1>
        <p className="page-subtitle">Введите код из QR, чтобы открыть карточку партии в рамках срока действия токена.</p>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
          <Input label="Код доступа" value={code} onChange={(event) => setCode(event.target.value)} placeholder="Введите код из QR..." />
          <Button onClick={() => checkMutation.mutate(code.trim())} loading={checkMutation.isPending} disabled={!code.trim()}>
            Проверить
          </Button>
        </div>
      </article>

      {error ? <ErrorState title="Проверка QR" description={error} /> : null}

      {foundBatch ? (
        <article className="surface p-5">
          <h2 className="font-heading text-xl text-brand-900">Найдена партия #{foundBatch.id}</h2>
          <div className="mt-3 grid gap-2 text-sm text-brand-900 md:grid-cols-2">
            <p>
              <span className="font-semibold">Тип:</span> {foundBatch.waste_type}
            </p>
            <p>
              <span className="font-semibold">Количество:</span> {foundBatch.quantity}
            </p>
            <p className="md:col-span-2">
              <span className="font-semibold">Адрес вывоза:</span> {foundBatch.pickup_point}
            </p>
            <p>
              <span className="font-semibold">Срок QR:</span> {formatDateTime(getQrExpiry(scannedQr ?? foundBatch.qr))}
            </p>
            <p>
              <span className="font-semibold">Статус:</span>{' '}
              <StatusBadge status={getBatchLatestStatus(foundBatch)} />
            </p>
          </div>
          <div className="mt-4">
            <Link to={`/app/driver/batches/${foundBatch.id}`}>
              <Button>Открыть карточку партии</Button>
            </Link>
          </div>
        </article>
      ) : null}
    </section>
  );
}
