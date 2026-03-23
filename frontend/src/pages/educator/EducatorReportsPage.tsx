import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listAllBatches } from '@/api/batches';
import { StatusBadge } from '@/components/shared';
import { Button, EmptyState, ErrorState, Input, Loader, Select, Table } from '@/components/ui';
import { formatDateTime } from '@/utils/date';
import { getBatchLatestStatus, getBatchLatestStatusTime } from '@/utils/batches';

function downloadCsv(content: string, name: string) {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}

export function EducatorReportsPage() {
  const [wasteType, setWasteType] = useState('');
  const [status, setStatus] = useState('');

  const batchesQuery = useQuery({
    queryKey: ['batches', 'educator', 'reports'],
    queryFn: () => listAllBatches(10),
  });

  const filtered = useMemo(() => {
    const source = batchesQuery.data ?? [];
    return source.filter((item) => {
      const latest = getBatchLatestStatus(item);
      const byType = wasteType ? item.waste_type.toLowerCase().includes(wasteType.toLowerCase()) : true;
      const byStatus = status ? latest === status : true;
      return byType && byStatus;
    });
  }, [batchesQuery.data, status, wasteType]);

  const exportCsv = () => {
    const lines = ['id,waste_type,quantity,pickup_point,status,updated_at'];
    filtered.forEach((item) => {
      const latestStatus = getBatchLatestStatus(item);
      const latestTime = getBatchLatestStatusTime(item);
      lines.push(
        [
          item.id,
          `"${item.waste_type.replaceAll('"', '""')}"`,
          item.quantity,
          `"${item.pickup_point.replaceAll('"', '""')}"`,
          latestStatus,
          latestTime ?? '',
        ].join(','),
      );
    });
    downloadCsv(lines.join('\n'), `educator-report-${new Date().toISOString().slice(0, 10)}.csv`);
  };

  if (batchesQuery.isLoading) {
    return <Loader label="Собираем отчет..." />;
  }

  if (batchesQuery.isError) {
    return <ErrorState onRetry={() => void batchesQuery.refetch()} />;
  }

  if (!filtered.length) {
    return <EmptyState title="Данных для отчета нет" description="Измените фильтры или создайте партии." />;
  }

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Отчеты образователя</h1>
        <p className="page-subtitle">Фильтрация и экспорт сводки по партиям в CSV.</p>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_auto] md:items-end">
          <Input label="Тип отходов" value={wasteType} onChange={(event) => setWasteType(event.target.value)} />
          <Select
            label="Статус"
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            placeholder="Все статусы"
            options={[
              { value: 'CREATED', label: 'Создана' },
              { value: 'IN_TRANSIT', label: 'В пути' },
              { value: 'DELIVERED', label: 'Доставлена' },
              { value: 'ACCEPTED', label: 'Принята' },
              { value: 'CANCELLED', label: 'Отменена' },
            ]}
          />
          <Button onClick={exportCsv}>Экспорт CSV</Button>
        </div>
      </article>

      <article className="surface p-5">
        <Table
          data={filtered}
          rowKey={(item) => item.id}
          columns={[
            { key: 'id', title: 'Номер', render: (item) => `#${item.id}` },
            { key: 'type', title: 'Тип', render: (item) => item.waste_type },
            { key: 'quantity', title: 'Количество', render: (item) => item.quantity },
            { key: 'pickup', title: 'Адрес вывоза', render: (item) => item.pickup_point },
            {
              key: 'status',
              title: 'Статус',
              render: (item) => <StatusBadge status={getBatchLatestStatus(item)} />,
            },
            {
              key: 'updated',
              title: 'Последнее обновление',
              render: (item) => formatDateTime(getBatchLatestStatusTime(item)),
            },
          ]}
        />
      </article>
    </section>
  );
}
