import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { listBatches } from '@/api/batches';
import { StatusBadge } from '@/components/shared';
import { Button, EmptyState, ErrorState, Input, Loader, Pagination, Table } from '@/components/ui';
import { formatDateTime } from '@/utils/date';
import { getBatchLatestStatus, getBatchLatestStatusTime } from '@/utils/batches';

export function EducatorBatchesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();
  const goToCreateBatch = () => navigate('/app/educator/batches/new');

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
        description="Создайте первую партию и выдайте водителю QR-код доступа."
        actionText="Создать партию"
        onAction={goToCreateBatch}
      />
    );
  }

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="page-title">Партии образователя</h1>
            <p className="page-subtitle">Просмотр статусов, QR-доступа и ключевых параметров партии.</p>
          </div>
          <Button type="button" onClick={goToCreateBatch}>
            Создать партию
          </Button>
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
              render: (item) => <StatusBadge status={getBatchLatestStatus(item)} />,
            },
            {
              key: 'updated',
              title: 'Обновлено',
              render: (item) => formatDateTime(getBatchLatestStatusTime(item)),
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
