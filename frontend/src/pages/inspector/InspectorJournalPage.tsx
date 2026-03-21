import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { listAuditLogs } from '@/api/audit';
import { Button, EmptyState, ErrorState, Input, Loader, Pagination, Table } from '@/components/ui';
import { formatDateTime } from '@/utils/date';

function exportCsv(rows: string[], fileName: string) {
  const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

export function InspectorJournalPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');

  const query = useQuery({
    queryKey: ['audit', page],
    queryFn: () => listAuditLogs(page),
  });

  const filtered = useMemo(() => {
    const source = query.data?.results ?? [];
    const value = search.trim().toLowerCase();
    if (!value) {
      return source;
    }
    return source.filter(
      (item) =>
        item.action.toLowerCase().includes(value) ||
        item.object_type.toLowerCase().includes(value) ||
        item.object_id.toLowerCase().includes(value) ||
        item.user_email?.toLowerCase().includes(value),
    );
  }, [query.data?.results, search]);

  const handleExport = () => {
    const lines = ['id,user_email,action,object_type,object_id,created_at'];
    filtered.forEach((row) => {
      lines.push([row.id, row.user_email ?? '', row.action, row.object_type, row.object_id, row.created_at].join(','));
    });
    exportCsv(lines, `audit-journal-${new Date().toISOString().slice(0, 10)}.csv`);
  };

  if (query.isLoading) {
    return <Loader label="Загружаем журнал..." />;
  }

  if (query.isError) {
    return <ErrorState onRetry={() => void query.refetch()} />;
  }

  if (!filtered.length) {
    return <EmptyState title="Журнал пуст" description="События появятся после активности пользователей." />;
  }

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Журнал инспектора</h1>
        <p className="page-subtitle">Единый аудит действий в системе.</p>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
          <Input label="Поиск" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="action, object_type, object_id..." />
          <Button onClick={handleExport}>Экспорт CSV</Button>
        </div>
      </article>

      <article className="surface p-5">
        <Table
          data={filtered}
          rowKey={(item) => item.id}
          columns={[
            { key: 'id', title: 'ID', render: (item) => item.id },
            { key: 'user', title: 'Пользователь', render: (item) => item.user_email || `user:${item.user ?? '—'}` },
            { key: 'action', title: 'Действие', render: (item) => item.action },
            { key: 'object', title: 'Объект', render: (item) => `${item.object_type}:${item.object_id}` },
            { key: 'created', title: 'Дата', render: (item) => formatDateTime(item.created_at) },
            {
              key: 'open',
              title: 'Открыть',
              render: (item) =>
                item.object_type.toLowerCase().includes('waste') ? (
                  <Link to={`/app/educator/batches/${item.object_id}`} className="text-sm font-semibold text-brand-700 underline-offset-2 hover:underline">
                    Карточка
                  </Link>
                ) : (
                  '—'
                ),
            },
          ]}
        />
        <div className="mt-4">
          <Pagination page={page} total={query.data?.count ?? filtered.length} onPageChange={setPage} />
        </div>
      </article>
    </section>
  );
}
