import type { UserRole } from '@/app/constants/roles';
import { ROLE_LABELS } from '@/app/constants/roles';
import { Badge } from '@/components/ui/Badge';

type RoleBadgeProps = {
  role: UserRole;
};

export function RoleBadge({ role }: RoleBadgeProps) {
  const tone = role === 'ADMIN' ? 'warning' : 'brand';
  return <Badge tone={tone}>{ROLE_LABELS[role]}</Badge>;
}
