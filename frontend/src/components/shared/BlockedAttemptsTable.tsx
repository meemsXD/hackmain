import { Table } from '@/components/ui/Table';
import { formatDateTime } from '@/utils/date';

export type BlockedAttempt = {
  id: string;
  code: string;
  reason: string;
  createdAt: string;
};

type BlockedAttemptsTableProps = {
  items: BlockedAttempt[];
};

export function BlockedAttemptsTable({ items }: BlockedAttemptsTableProps) {
  if (!items.length) {
    return <p className="text-sm text-brand-700">Заблокированных попыток нет.</p>;
  }

  return (
    <Table
      data={items}
      rowKey={(item) => item.id}
      columns={[
        { key: 'code', title: 'Код', render: (item) => item.code },
        { key: 'reason', title: 'Причина', render: (item) => item.reason },
        { key: 'createdAt', title: 'Дата', render: (item) => formatDateTime(item.createdAt) },
      ]}
    />
  );
}
