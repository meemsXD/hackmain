import { useMemo, useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { TEXTS } from '@/app/constants/texts';
import { Button, Drawer } from '@/components/ui';
import { RoleBadge } from '@/components/shared';
import { useAuth } from '@/auth/useAuth';
import type { UserRole } from '@/app/constants/roles';

type NavItem = {
  to: string;
  label: string;
  roles?: UserRole[];
  external?: boolean;
};

const NAV_ITEMS: NavItem[] = [
  { to: '/app/profile', label: 'Профиль' },
  { to: '/app/educator/batches', label: 'Партии', roles: ['RECYCLER'] },
  { to: '/app/educator/reports', label: 'Отчеты', roles: ['RECYCLER'] },
  { to: '/app/driver/access', label: 'Доступ по коду', roles: ['DRIVER'] },
  { to: '/app/driver/batches', label: 'Мои активные партии', roles: ['DRIVER'] },
  { to: '/app/processor/batches', label: 'Входящие партии', roles: ['MEDICAL'] },
  { to: '/app/processor/drivers', label: 'Водители', roles: ['MEDICAL'] },
  { to: '/app/inspector/journal', label: 'Журнал', roles: ['INSPECTOR'] },
  { to: '/app/inspector/reports', label: 'Отчеты инспектора', roles: ['INSPECTOR'] },
  { to: import.meta.env.VITE_ADMIN_URL ?? 'http://localhost:8001/admin/', label: 'Админ-панель', roles: ['ADMIN'], external: true },
];

function isAllowed(roles: UserRole[], item: NavItem) {
  if (!item.roles?.length) {
    return true;
  }
  return item.roles.some((role) => roles.includes(role));
}

export function AppLayout() {
  const { user, roles, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const menuItems = useMemo(() => NAV_ITEMS.filter((item) => isAllowed(roles, item)), [roles]);

  return (
    <div className="min-h-screen">
      <header className="border-b border-brand-100/80 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-[1320px] items-center justify-between gap-4 px-4 py-3 md:px-6">
          <div>
            <p className="font-heading text-lg text-brand-900">{TEXTS.appName}</p>
            <p className="text-xs text-brand-700">Единый контур движения медицинских отходов</p>
          </div>
          <div className="hidden items-center gap-2 md:flex">
            {roles.map((role) => (
              <RoleBadge key={role} role={role} />
            ))}
            <Button variant="ghost" size="sm" onClick={() => void logout()}>
              Выйти
            </Button>
          </div>
          <Button className="md:hidden" variant="secondary" size="sm" onClick={() => setMobileOpen(true)}>
            Меню
          </Button>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1320px] gap-4 px-4 py-4 md:grid-cols-[290px_1fr] md:px-6">
        <aside className="surface hidden h-fit p-3 md:block">
          <div className="mb-4 rounded-2xl bg-brand-50 p-3">
            <p className="text-xs uppercase tracking-wide text-brand-700">Пользователь</p>
            <p className="mt-1 font-semibold text-brand-900">{user?.full_name ?? '-'}</p>
            <p className="text-sm text-brand-700">{user?.login ?? ''}</p>
          </div>
          <nav className="space-y-1">
            {menuItems.map((item) =>
              item.external ? (
                <a
                  key={item.to}
                  href={item.to}
                  target="_blank"
                  rel="noreferrer"
                  className="block rounded-lg px-3 py-2 text-sm text-brand-800 transition hover:bg-brand-50"
                >
                  {item.label}
                </a>
              ) : (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `block rounded-lg px-3 py-2 text-sm transition ${
                      isActive ? 'bg-brand-100 font-semibold text-brand-900' : 'text-brand-800 hover:bg-brand-50'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ),
            )}
          </nav>
        </aside>

        <main className="space-y-4">
          <Outlet />
        </main>
      </div>

      <Drawer
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        title={user?.full_name ?? 'Навигация'}
        headerExtra={
          <Button variant="ghost" size="sm" onClick={() => setMobileOpen(false)}>
            Закрыть
          </Button>
        }
      >
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {roles.map((role) => (
              <RoleBadge key={role} role={role} />
            ))}
          </div>
          <nav className="space-y-1">
            {menuItems.map((item) =>
              item.external ? (
                <a
                  key={item.to}
                  href={item.to}
                  target="_blank"
                  rel="noreferrer"
                  className="block rounded-lg px-3 py-2 text-sm text-brand-800 transition hover:bg-brand-50"
                >
                  {item.label}
                </a>
              ) : (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    `block rounded-lg px-3 py-2 text-sm transition ${
                      isActive ? 'bg-brand-100 font-semibold text-brand-900' : 'text-brand-800 hover:bg-brand-50'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ),
            )}
          </nav>
          <Button fullWidth variant="ghost" onClick={() => void logout()}>
            Выйти
          </Button>
        </div>
      </Drawer>
    </div>
  );
}

