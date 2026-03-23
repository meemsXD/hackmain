import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { scanQrCode } from '@/api/batches';
import { getApiErrorMessage } from '@/api/client';
import { StatusBadge } from '@/components/shared';
import { Button, ErrorState, Loader } from '@/components/ui';
import { formatDateTime } from '@/utils/date';
import { getBatchLatestStatus, getQrExpiry } from '@/utils/batches';

export function DriverAccessTokenPage() {
  const { token = '' } = useParams<{ token: string }>();

  const scanQuery = useQuery({
    queryKey: ['qr-token-scan', token],
    queryFn: () => scanQrCode({ code: token }),
    enabled: Boolean(token),
    retry: false,
  });

  if (!token) {
    return (
      <main className="grid min-h-screen place-items-center px-4">
        <section className="surface w-full max-w-xl p-6">
          <ErrorState title="QR-токен не найден" description="В ссылке отсутствует код доступа." />
        </section>
      </main>
    );
  }

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <section className="surface w-full max-w-xl p-6">
        <h1 className="font-heading text-3xl text-brand-900">Доступ водителя по QR</h1>
        <p className="mt-2 text-sm text-brand-700">Токен из ссылки проверяется через API в режиме реального времени.</p>

        <div className="mt-4 rounded-xl bg-brand-50 p-3 text-sm text-brand-900">
          <p className="font-semibold">Код:</p>
          <p className="mt-1 break-all">{token}</p>
        </div>

        <div className="mt-4">
          {scanQuery.isLoading ? <Loader label="Проверяем QR..." /> : null}
          {scanQuery.isError ? <ErrorState title="Доступ по QR" description={getApiErrorMessage(scanQuery.error)} /> : null}

          {scanQuery.data ? (
            <div className="space-y-2 text-sm text-brand-900">
              <p>
                <span className="font-semibold">Партия:</span> #{scanQuery.data.batch.id}
              </p>
              <p>
                <span className="font-semibold">Тип:</span> {scanQuery.data.batch.waste_type}
              </p>
              <p>
                <span className="font-semibold">Количество:</span> {scanQuery.data.batch.quantity}
              </p>
              <p>
                <span className="font-semibold">Срок QR:</span> {formatDateTime(getQrExpiry(scanQuery.data.qr))}
              </p>
              <p>
                <span className="font-semibold">Статус:</span> <StatusBadge status={getBatchLatestStatus(scanQuery.data.batch)} />
              </p>
            </div>
          ) : null}
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Link to="/login">
            <Button>Войти в систему</Button>
          </Link>
          <Link to={`/app/driver/access?code=${encodeURIComponent(token)}`}>
            <Button variant="secondary">Открыть экран доступа</Button>
          </Link>
        </div>
      </section>
    </main>
  );
}
