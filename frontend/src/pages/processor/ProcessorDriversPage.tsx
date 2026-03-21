import { useAuth } from '@/auth/useAuth';
import { EmptyState, Table } from '@/components/ui';

export function ProcessorDriversPage() {
  const { user } = useAuth();
  const driverIds = user?.processor_profile?.drivers ?? [];

  if (!driverIds.length) {
    return (
      <EmptyState
        title="Список водителей пуст"
        description="Backend не возвращает карточки водителей отдельным endpoint, но IDs появятся здесь при привязке."
      />
    );
  }

  return (
    <section className="surface p-5">
      <h1 className="page-title">Водители организации</h1>
      <p className="page-subtitle">MVP режим: просмотр ID водителей из профиля переработчика.</p>
      <div className="mt-4">
        <Table
          data={driverIds.map((id) => ({ id }))}
          rowKey={(item) => item.id}
          columns={[
            { key: 'id', title: 'ID водителя', render: (item) => item.id },
            { key: 'status', title: 'Статус', render: () => 'Активный/неизвестно' },
          ]}
        />
      </div>
    </section>
  );
}
