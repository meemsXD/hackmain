import { STATUS_LABELS } from '@/app/constants/roles';
import { Badge } from '@/components/ui/Badge';

type StatusBadgeProps = {
  status: string;
};

const toneMap: Record<string, 'neutral' | 'brand' | 'warning' | 'success' | 'danger'> = {
  CREATED: 'brand',
  IN_TRANSIT: 'warning',
  DELIVERED: 'warning',
  ACCEPTED: 'success',
  CANCELLED: 'danger',
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return <Badge tone={toneMap[status] ?? 'neutral'}>{STATUS_LABELS[status] ?? status}</Badge>;
}
