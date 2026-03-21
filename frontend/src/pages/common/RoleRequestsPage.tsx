import { useMemo, useState } from 'react';
import type { UserRole } from '@/app/constants/roles';
import { ROLE_LABELS } from '@/app/constants/roles';
import { useAuth } from '@/auth/useAuth';
import { createRoleRequest, loadRoleRequests } from '@/features/roleRequests/storage';
import { Badge, Button, Select, Table, Textarea } from '@/components/ui';
import { formatDateTime } from '@/utils/date';

export function RoleRequestsPage() {
  const { roles } = useAuth();
  const [selectedRole, setSelectedRole] = useState<UserRole>('DRIVER');
  const [comment, setComment] = useState('');
  const [requests, setRequests] = useState(loadRoleRequests());

  const availableRoles = useMemo(() => {
    const allRoles: UserRole[] = ['RECYCLER', 'DRIVER', 'MEDICAL', 'INSPECTOR'];
    return allRoles.filter((role) => !roles.includes(role));
  }, [roles]);

  const handleSubmit = () => {
    if (!comment.trim()) {
      return;
    }
    const next = createRoleRequest(selectedRole, comment.trim());
    setRequests([next, ...requests]);
    setComment('');
  };

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Мои заявки на роли</h1>
        <p className="page-subtitle">В текущем backend нет отдельного endpoint для заявок, поэтому используется локальный draft-реестр.</p>

        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_2fr_auto] md:items-end">
          <Select
            label="Новая роль"
            options={availableRoles.map((role) => ({ value: role, label: ROLE_LABELS[role] }))}
            value={selectedRole}
            onChange={(event) => setSelectedRole(event.target.value as UserRole)}
          />
          <Textarea label="Комментарий" value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Зачем вам нужна роль..." />
          <Button onClick={handleSubmit} disabled={!availableRoles.length || !comment.trim()}>
            Отправить
          </Button>
        </div>
      </article>

      <article className="surface p-5">
        <h2 className="font-heading text-xl text-brand-900">История заявок</h2>
        {!requests.length ? (
          <p className="mt-3 text-sm text-brand-700">Заявок пока нет.</p>
        ) : (
          <div className="mt-3">
            <Table
              data={requests}
              rowKey={(item) => item.id}
              columns={[
                { key: 'role', title: 'Роль', render: (item) => ROLE_LABELS[item.role] },
                { key: 'comment', title: 'Комментарий', render: (item) => item.comment },
                {
                  key: 'status',
                  title: 'Статус',
                  render: (item) => <Badge tone={item.status === 'PENDING' ? 'warning' : 'success'}>{item.status}</Badge>,
                },
                { key: 'createdAt', title: 'Дата', render: (item) => formatDateTime(item.createdAt) },
              ]}
            />
          </div>
        )}
      </article>
    </section>
  );
}
