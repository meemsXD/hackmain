import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { listBatches } from '@/api/batches';
import { StatusBadge } from '@/components/shared';
import { EmptyState, ErrorState, Loader, Pagination, Table } from '@/components/ui';
import { formatDateTime } from '@/utils/date';

const ACTIVE_STATES = ['CREATED', 'IN_TRANSIT', 'DELIVERED'];

export function DriverBatchesPage() {
  const [page, setPage] = useState(1);

  const query = useQuery({
    queryKey: ['batches', 'driver', page],
    queryFn: () => listBatches(page),
  });

  const active = useMemo(() => {
    const rows = query.data?.results ?? [];
    return rows.filter((item) => ACTIVE_STATES.includes(item.statuses[item.statuses.length - 1]?.state ?? 'CREATED'));
  }, [query.data?.results]);

  if (query.isLoading) {
    return <Loader label="Загружаем активные партии..." />;
  }

  if (query.isError) {
    return <ErrorState onRetry={() => void query.refetch()} />;
  }

  if (!active.length) {
    return <EmptyState title="Активных партий нет" description="Как только образователь создаст партию и выдаст вам доступ, она появится здесь." />;
  }

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Мои активные партии</h1>
        <p className="page-subtitle">Отсюда водитель подтверждает забор и доставку.</p>
      </article>
      <article className="surface p-5">
        <Table
          data={active}
          rowKey={(item) => item.id}
          columns={[
            { key: 'id', title: 'Номер', render: (item) => `#${item.id}` },
            { key: 'type', title: 'Тип', render: (item) => item.waste_type },
            { key: 'quantity', title: 'Количество', render: (item) => item.quantity },
            { key: 'pickup', title: 'Адрес вывоза', render: (item) => item.pickup_point },
            { key: 'status', title: 'Статус', render: (item) => <StatusBadge status={item.statuses[item.statuses.length - 1]?.state ?? 'CREATED'} /> },
            { key: 'updated', title: 'Обновлено', render: (item) => formatDateTime(item.statuses[item.statuses.length - 1]?.time ?? null) },
            {
              key: 'action',
              title: 'Действие',
              render: (item) => (
                <Link to={`/app/driver/batches/${item.id}`} className="text-sm font-semibold text-brand-700 underline-offset-2 hover:underline">
                  Открыть
                </Link>
              ),
            },
          ]}
        />
        <div className="mt-4">
          <Pagination page={page} total={query.data?.count ?? active.length} onPageChange={setPage} />
        </div>
      </article>
    </section>
  );
}
