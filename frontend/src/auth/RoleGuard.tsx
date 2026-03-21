import { Navigate, Outlet, useLocation } from 'react-router-dom';
import type { UserRole } from '@/app/constants/roles';
import { useAuth } from '@/auth/useAuth';
import { getDefaultHomePath } from '@/utils/roles';

type RoleGuardProps = {
  allow: UserRole[];
};

export function RoleGuard({ allow }: RoleGuardProps) {
  const { roles } = useAuth();
  const location = useLocation();
  const hasAccess = roles.some((role) => allow.includes(role));

  if (!hasAccess) {
    return <Navigate to={getDefaultHomePath(roles)} replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
