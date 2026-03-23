import { Table } from '@/components/ui/Table';
import { formatDateTime } from '@/utils/date';

const REASON_LABELS: Record<string, string> = {
  QR_NOT_FOUND: 'QR-код не найден',
  QR_EXPIRED: 'Срок действия QR истек',
  QR_INACTIVE: 'QR-код деактивирован',
  ACCESS_BLOCKED: 'Доступ заблокирован',
};

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
        { key: 'reason', title: 'Причина', render: (item) => REASON_LABELS[item.reason] ?? item.reason },
        { key: 'createdAt', title: 'Дата', render: (item) => formatDateTime(item.createdAt) },
      ]}
    />
  );
}
