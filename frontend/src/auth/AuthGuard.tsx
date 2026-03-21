import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/auth/useAuth';
import { Loader } from '@/components/ui/Loader';

export function AuthGuard() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === 'loading') {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader label="Проверяем сессию..." />
      </div>
    );
  }

  if (status === 'unauthenticated' || status === 'session_expired') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
