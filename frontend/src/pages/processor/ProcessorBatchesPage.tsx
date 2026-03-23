import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { listAllBatches } from '@/api/batches';
import { StatusBadge } from '@/components/shared';
import { EmptyState, ErrorState, Input, Loader, Select, Table } from '@/components/ui';
import { getBatchLatestStatus } from '@/utils/batches';

export function ProcessorBatchesPage() {
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');

  const query = useQuery({
    queryKey: ['batches', 'processor'],
    queryFn: () => listAllBatches(10),
  });

  const filtered = useMemo(() => {
    const source = query.data ?? [];
    return source.filter((item) => {
      const latest = getBatchLatestStatus(item);
      const byStatus = status ? latest === status : true;
      const bySearch = search ? item.waste_type.toLowerCase().includes(search.toLowerCase()) || String(item.id).includes(search) : true;
      return byStatus && bySearch;
    });
  }, [query.data, search, status]);

  if (query.isLoading) {
    return <Loader label="Загружаем входящие партии..." />;
  }

  if (query.isError) {
    return <ErrorState onRetry={() => void query.refetch()} />;
  }

  if (!filtered.length) {
    return <EmptyState title="Входящих партий нет" description="Измените фильтры или дождитесь новых поставок." />;
  }

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Входящие партии</h1>
        <p className="page-subtitle">Рабочий экран переработчика для приемки.</p>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <Input label="Поиск по номеру или типу" value={search} onChange={(event) => setSearch(event.target.value)} />
          <Select
            label="Статус"
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            placeholder="Все"
            options={[
              { value: 'CREATED', label: 'Создана' },
              { value: 'IN_TRANSIT', label: 'В пути' },
              { value: 'DELIVERED', label: 'Доставлена' },
              { value: 'ACCEPTED', label: 'Принята' },
              { value: 'CANCELLED', label: 'Отменена' },
            ]}
          />
        </div>
      </article>
      <article className="surface p-5">
        <Table
          data={filtered}
          rowKey={(item) => item.id}
          columns={[
            { key: 'id', title: 'Номер', render: (item) => `#${item.id}` },
            { key: 'type', title: 'Тип отходов', render: (item) => item.waste_type },
            { key: 'quantity', title: 'Количество', render: (item) => item.quantity },
            { key: 'pickup', title: 'Адрес вывоза', render: (item) => item.pickup_point },
            { key: 'status', title: 'Статус', render: (item) => <StatusBadge status={getBatchLatestStatus(item)} /> },
            {
              key: 'action',
              title: 'Действие',
              render: (item) => (
                <Link to={`/app/processor/batches/${item.id}`} className="text-sm font-semibold text-brand-700 underline-offset-2 hover:underline">
                  Открыть
                </Link>
              ),
            },
          ]}
        />
      </article>
    </section>
  );
}
