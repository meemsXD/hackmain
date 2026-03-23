import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listOrganizations } from '@/api/organizations';
import { useAuth } from '@/auth/useAuth';
import { OrganizationSummaryCard, RoleBadge } from '@/components/shared';
import { Button, Input } from '@/components/ui';

function generateSignatureToken(): string {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const randomBytes = new Uint8Array(10);
  crypto.getRandomValues(randomBytes);
  const token = Array.from(randomBytes, (value) => alphabet[value % alphabet.length]).join('');
  return `SIG-${token}`;
}

export function ProfilePage() {
  const { user, roles, refreshUser, signatureToken, saveSignatureToken } = useAuth();
  const [copied, setCopied] = useState(false);
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

  const handleGenerateToken = () => {
    const next = generateSignatureToken();
    saveSignatureToken(next);
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1800);
  };

  const handleCopyToken = async () => {
    if (!signatureToken) {
      return;
    }
    await navigator.clipboard.writeText(signatureToken);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1400);
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
            {organization ? (
              <p className="text-sm">
                <span className="font-semibold">Организация:</span> {organization.name}
              </p>
            ) : null}
            <div className="flex flex-wrap gap-2">
              {roles.map((role) => (
                <RoleBadge key={role} role={role} />
              ))}
            </div>
          </div>

          <div className="space-y-2 rounded-xl bg-brand-50 p-4">
            <p className="text-xs uppercase tracking-wide text-brand-700">Профиль роли</p>

            {user?.driver_profile ? (
              <>
                <p className="text-sm">
                  <span className="font-semibold">Роль водителя:</span> активна
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Номер ТС:</span> {user.driver_profile.vehicle_number || '—'}
                </p>
              </>
            ) : null}

            {user?.educator_profile ? (
              <>
                <p className="text-sm">
                  <span className="font-semibold">Лицензия образователя:</span>{' '}
                  {user.educator_profile.license_number || '—'}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Адрес образователя:</span> {user.educator_profile.address || '—'}
                </p>
              </>
            ) : null}

            {user?.processor_profile ? (
              <>
                <p className="text-sm">
                  <span className="font-semibold">Лицензия переработчика:</span>{' '}
                  {user.processor_profile.license_number || '—'}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Адрес площадки:</span>{' '}
                  {user.processor_profile.facility_address || '—'}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Привязано водителей:</span>{' '}
                  {user.processor_profile.drivers?.length ?? 0}
                </p>
              </>
            ) : null}

            {!user?.driver_profile && !user?.educator_profile && !user?.processor_profile ? (
              <p className="text-sm text-brand-700">Дополнительные профильные данные пока отсутствуют.</p>
            ) : null}
          </div>

          <div className="space-y-2 rounded-xl bg-accent-100 p-4 md:col-span-2">
            <p className="text-xs uppercase tracking-wide text-accent-800">Токен подписи</p>
            <Input
              label="Токен для критичных действий"
              type="text"
              readOnly
              value={signatureToken}
              hint="Создается автоматически. Хранится локально в браузере."
            />
            <div className="flex flex-wrap gap-2">
              <Button onClick={handleCopyToken}>Копировать токен</Button>
              <Button variant="secondary" onClick={handleGenerateToken}>
                Сгенерировать новый
              </Button>
              <Button variant="ghost" onClick={() => void refreshUser()}>
                Обновить профиль
              </Button>
            </div>
            {saved ? <p className="text-sm text-emerald-700">Новый токен сохранен.</p> : null}
            {copied ? <p className="text-sm text-emerald-700">Токен скопирован в буфер.</p> : null}
          </div>
        </div>
      </article>

      <OrganizationSummaryCard organization={organization} />
    </section>
  );
}
