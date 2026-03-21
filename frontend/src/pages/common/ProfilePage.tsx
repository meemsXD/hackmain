import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listOrganizations } from '@/api/organizations';
import { useAuth } from '@/auth/useAuth';
import { OrganizationSummaryCard, RoleBadge } from '@/components/shared';
import { Button, Input } from '@/components/ui';

export function ProfilePage() {
  const { user, roles, refreshUser, signatureToken, saveSignatureToken } = useAuth();
  const [tokenDraft, setTokenDraft] = useState(signatureToken);
  const [saved, setSaved] = useState(false);

  const organizationsQuery = useQuery({
    queryKey: ['organizations', 'profile'],
    queryFn: () => listOrganizations(1),
  });

  const organization = useMemo(() => {
    if (!user?.organization) {
      return null;
    }
    return organizationsQuery.data?.results.find((item) => item.id === user.organization) ?? null;
  }, [organizationsQuery.data?.results, user?.organization]);

  const handleSaveSignatureToken = () => {
    saveSignatureToken(tokenDraft.trim());
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1800);
  };

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Профиль</h1>
        <p className="page-subtitle">Просмотр и обновление персональных настроек.</p>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <div className="space-y-2 rounded-xl bg-brand-50 p-4">
            <p className="text-xs uppercase tracking-wide text-brand-700">Основные данные</p>
            <p className="text-sm">
              <span className="font-semibold">ФИО:</span> {user?.full_name ?? '—'}
            </p>
            <p className="text-sm">
              <span className="font-semibold">Логин:</span> {user?.login ?? '—'}
            </p>
            <div className="flex flex-wrap gap-2">
              {roles.map((role) => (
                <RoleBadge key={role} role={role} />
              ))}
            </div>
          </div>

          <div className="space-y-2 rounded-xl bg-accent-100 p-4">
            <p className="text-xs uppercase tracking-wide text-accent-800">Токен подписи</p>
            <Input
              label="Токен для критичных действий"
              type="password"
              value={tokenDraft}
              onChange={(event) => setTokenDraft(event.target.value)}
              hint="Сохраняется локально в браузере."
            />
            <div className="flex gap-2">
              <Button onClick={handleSaveSignatureToken}>Сохранить токен</Button>
              <Button variant="ghost" onClick={() => void refreshUser()}>
                Обновить профиль
              </Button>
            </div>
            {saved ? <p className="text-sm text-emerald-700">Токен сохранен.</p> : null}
          </div>
        </div>
      </article>

      <OrganizationSummaryCard organization={organization} />
    </section>
  );
}
