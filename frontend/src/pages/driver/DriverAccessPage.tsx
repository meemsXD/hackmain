import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { listAllBatches } from '@/api/batches';
import type { WasteBatch } from '@/api/types';
import { isExpired } from '@/utils/date';
import { StatusBadge } from '@/components/shared';
import { Button, ErrorState, Input } from '@/components/ui';

export function DriverAccessPage() {
  const [code, setCode] = useState('');
  const [foundBatch, setFoundBatch] = useState<WasteBatch | null>(null);
  const [error, setError] = useState('');

  const checkMutation = useMutation({
    mutationFn: async (value: string) => {
      const all = await listAllBatches(12);
      return all.find((item) => item.qr?.code === value) ?? null;
    },
    onSuccess: (batch) => {
      if (!batch) {
        setError('Партия по этому коду не найдена.');
        setFoundBatch(null);
        return;
      }
      if (!batch.qr || !batch.qr.is_active || isExpired(batch.qr.time)) {
        setError('Код найден, но срок доступа истек.');
        setFoundBatch(batch);
        return;
      }
      setError('');
      setFoundBatch(batch);
    },
    onError: () => {
      setError('Не удалось проверить код. Попробуйте еще раз.');
      setFoundBatch(null);
    },
  });

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Доступ по коду</h1>
        <p className="page-subtitle">Вставьте код из QR, чтобы открыть активную партию.</p>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
          <Input label="Код доступа" value={code} onChange={(event) => setCode(event.target.value)} placeholder="Введите код из QR..." />
          <Button onClick={() => checkMutation.mutate(code.trim())} loading={checkMutation.isPending} disabled={!code.trim()}>
            Проверить
          </Button>
        </div>
      </article>

      {error ? <ErrorState title="Проверка кода" description={error} /> : null}

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
              <span className="font-semibold">Статус:</span>{' '}
              <StatusBadge status={foundBatch.statuses[foundBatch.statuses.length - 1]?.state ?? 'CREATED'} />
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
