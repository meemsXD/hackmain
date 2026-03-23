import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listAuditLogs } from '@/api/audit';
import { listAllBatches } from '@/api/batches';
import { Button, ErrorState, Loader, Table } from '@/components/ui';
import { getBatchLatestStatus } from '@/utils/batches';

type SummaryRow = {
  key: string;
  title: string;
  value: number;
};

function downloadFile(content: string, filename: string, mimeType = 'application/json') {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function InspectorReportsPage() {
  const batchQuery = useQuery({
    queryKey: ['reports', 'inspector', 'batches'],
    queryFn: () => listAllBatches(10),
  });

  const auditQuery = useQuery({
    queryKey: ['reports', 'inspector', 'audit'],
    queryFn: () => listAuditLogs(1),
  });

  const summary = useMemo<SummaryRow[]>(() => {
    const batches = batchQuery.data ?? [];
    const logs = auditQuery.data?.results ?? [];

    const statusCount = batches.reduce<Record<string, number>>((acc, batch) => {
      const latest = getBatchLatestStatus(batch);
      acc[latest] = (acc[latest] ?? 0) + 1;
      return acc;
    }, {});

    return [
      { key: 'batches', title: 'Всего партий', value: batches.length },
      { key: 'audit', title: 'Событий аудита (страница 1)', value: logs.length },
      { key: 'created', title: 'Создано', value: statusCount.CREATED ?? 0 },
      { key: 'transit', title: 'В пути', value: statusCount.IN_TRANSIT ?? 0 },
      { key: 'delivered', title: 'Доставлено', value: statusCount.DELIVERED ?? 0 },
      { key: 'accepted', title: 'Принято', value: statusCount.ACCEPTED ?? 0 },
      { key: 'cancelled', title: 'Отменено', value: statusCount.CANCELLED ?? 0 },
    ];
  }, [auditQuery.data?.results, batchQuery.data]);

  if (batchQuery.isLoading || auditQuery.isLoading) {
    return <Loader label="Формируем отчет..." />;
  }

  if (batchQuery.isError || auditQuery.isError) {
    return <ErrorState onRetry={() => void batchQuery.refetch()} />;
  }

  const exportJson = () => {
    downloadFile(JSON.stringify(summary, null, 2), `inspector-summary-${new Date().toISOString().slice(0, 10)}.json`);
  };

  const exportCsv = () => {
    const lines = ['metric,value'];
    summary.forEach((row) => lines.push(`${row.title},${row.value}`));
    downloadFile(lines.join('\n'), `inspector-summary-${new Date().toISOString().slice(0, 10)}.csv`, 'text/csv;charset=utf-8;');
  };

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Отчеты инспектора</h1>
        <p className="page-subtitle">Сводка по партиям и журналу с экспортом в CSV/JSON.</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button onClick={exportCsv}>Экспорт CSV</Button>
          <Button variant="secondary" onClick={exportJson}>
            Экспорт JSON
          </Button>
        </div>
      </article>

      <article className="surface p-5">
        <Table
          data={summary}
          rowKey={(row) => row.key}
          columns={[
            { key: 'title', title: 'Метрика', render: (row) => row.title },
            { key: 'value', title: 'Значение', render: (row) => row.value },
          ]}
        />
      </article>
    </section>
  );
}
