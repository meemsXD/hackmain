import type { BatchStatus } from '@/api/types';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { formatDateTime } from '@/utils/date';

type BatchTimelineProps = {
  statuses: BatchStatus[];
};

export function BatchTimeline({ statuses }: BatchTimelineProps) {
  const sorted = [...statuses].sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());

  return (
    <div className="surface p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-brand-700">Таймлайн партии</h3>
      {!sorted.length ? (
        <p className="text-sm text-brand-600">Статусы пока отсутствуют.</p>
      ) : (
        <ol className="space-y-3">
          {sorted.map((status, index) => (
            <li key={status.id} className="relative pl-6">
              <span className="absolute left-0 top-2 h-2 w-2 rounded-full bg-brand-500" />
              {index < sorted.length - 1 ? <span className="absolute left-[3px] top-4 h-8 w-[2px] bg-brand-100" /> : null}
              <div className="flex items-center gap-2">
                <StatusBadge status={status.state} />
                <span className="text-xs text-brand-600">{formatDateTime(status.time)}</span>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
