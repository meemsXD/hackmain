import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { listBatches } from '@/api/batches';
import { StatusBadge } from '@/components/shared';
import { Button, EmptyState, ErrorState, Input, Loader, Pagination, Table } from '@/components/ui';
import { formatDateTime } from '@/utils/date';

export function EducatorBatchesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const batchesQuery = useQuery({
    queryKey: ['batches', 'educator', page],
    queryFn: () => listBatches(page),
  });

  const filtered = useMemo(() => {
    const items = batchesQuery.data?.results ?? [];
    const value = search.trim().toLowerCase();
    if (!value) {
      return items;
    }
    return items.filter((item) => item.waste_type.toLowerCase().includes(value) || String(item.id).includes(value));
  }, [batchesQuery.data?.results, search]);

  if (batchesQuery.isLoading) {
    return <Loader label="Загружаем партии..." />;
  }

  if (batchesQuery.isError) {
    return <ErrorState onRetry={() => void batchesQuery.refetch()} />;
  }

  const data = batchesQuery.data;
  if (!data || !data.results.length) {
    return (
      <EmptyState
        title="Партии пока не созданы"
        description="Создайте первую партию и выдайте QR-код для водителя."
        actionText="Создать партию"
        onAction={() => navigate('/app/educator/batches/new')}
      />
    );
  }

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="page-title">Партии образовательной организации</h1>
            <p className="page-subtitle">Список партий, QR-доступ и ключевые статусы движения.</p>
          </div>
          <Link to="/app/educator/batches/new">
            <Button>Создать партию</Button>
          </Link>
        </div>

        <div className="mt-4 max-w-md">
          <Input label="Поиск по типу или номеру" value={search} onChange={(event) => setSearch(event.target.value)} />
        </div>
      </article>

      <article className="surface p-5">
        <Table
          data={filtered}
          rowKey={(item) => item.id}
          columns={[
            { key: 'id', title: 'Номер', render: (item) => `#${item.id}` },
            { key: 'wasteType', title: 'Тип отходов', render: (item) => item.waste_type },
            { key: 'quantity', title: 'Количество', render: (item) => item.quantity },
            { key: 'pickup', title: 'Адрес вывоза', render: (item) => item.pickup_point },
            {
              key: 'status',
              title: 'Статус',
              render: (item) => <StatusBadge status={item.statuses[item.statuses.length - 1]?.state ?? 'CREATED'} />,
            },
            {
              key: 'updated',
              title: 'Обновлено',
              render: (item) => formatDateTime(item.statuses[item.statuses.length - 1]?.time ?? null),
            },
            {
              key: 'action',
              title: 'Действие',
              render: (item) => (
                <Link className="text-sm font-semibold text-brand-700 underline-offset-2 hover:underline" to={`/app/educator/batches/${item.id}`}>
                  Открыть
                </Link>
              ),
            },
          ]}
        />
        <div className="mt-4">
          <Pagination page={page} total={data.count} onPageChange={setPage} />
        </div>
      </article>
    </section>
  );
}
