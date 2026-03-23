import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { assignProcessorDriver, createProcessorDriver, listProcessorDrivers, unassignProcessorDriver } from '@/api/users';
import { getApiErrorMessage } from '@/api/client';
import { useAuth } from '@/auth/useAuth';
import { Button, EmptyState, ErrorState, Input, Loader, Table } from '@/components/ui';

export function ProcessorDriversPage() {
  const { user } = useAuth();
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [driverName, setDriverName] = useState('');
  const [driverLogin, setDriverLogin] = useState('');
  const [driverPassword, setDriverPassword] = useState('');
  const [attachDriverId, setAttachDriverId] = useState('');
  const [actionError, setActionError] = useState('');

  const driversQuery = useQuery({
    queryKey: ['processor', 'drivers'],
    queryFn: () => listProcessorDrivers(),
  });

  const createMutation = useMutation({
    mutationFn: createProcessorDriver,
    onSuccess: async () => {
      setActionError('');
      setVehicleNumber('');
      setDriverName('');
      setDriverLogin('');
      setDriverPassword('');
      await driversQuery.refetch();
    },
    onError: (error) => {
      setActionError(getApiErrorMessage(error));
    },
  });

  const attachMutation = useMutation({
    mutationFn: (driverId: number) => assignProcessorDriver(driverId),
    onSuccess: async () => {
      setActionError('');
      setAttachDriverId('');
      await driversQuery.refetch();
    },
    onError: (error) => {
      setActionError(getApiErrorMessage(error));
    },
  });

  const detachMutation = useMutation({
    mutationFn: (driverId: number) => unassignProcessorDriver(driverId),
    onSuccess: async () => {
      setActionError('');
      await driversQuery.refetch();
    },
    onError: (error) => {
      setActionError(getApiErrorMessage(error));
    },
  });

  const handleCreate = async () => {
    const payload: {
      vehicle_number: string;
      full_name?: string;
      login?: string;
      password?: string;
    } = {
      vehicle_number: vehicleNumber.trim(),
    };

    if (!payload.vehicle_number) {
      setActionError('Укажите номер ТС.');
      return;
    }

    const hasUserFields = driverName.trim() || driverLogin.trim() || driverPassword.trim();
    if (hasUserFields) {
      payload.full_name = driverName.trim();
      payload.login = driverLogin.trim();
      payload.password = driverPassword;
    }

    await createMutation.mutateAsync(payload);
  };

  const handleAttach = async () => {
    const id = Number(attachDriverId);
    if (!Number.isInteger(id) || id <= 0) {
      setActionError('Укажите корректный ID водителя.');
      return;
    }
    await attachMutation.mutateAsync(id);
  };

  if (!user?.processor_profile) {
    return <ErrorState title="Профиль недоступен" description="Профиль переработчика не найден у текущего пользователя." />;
  }

  if (driversQuery.isLoading) {
    return <Loader label="Загружаем карточки водителей..." />;
  }

  if (driversQuery.isError) {
    return <ErrorState title="Ошибка" description="Не удалось загрузить водителей." onRetry={() => void driversQuery.refetch()} />;
  }

  const data = driversQuery.data ?? [];

  return (
    <section className="space-y-4">
      <article className="surface p-5">
        <h1 className="page-title">Водители переработчика</h1>
        <p className="page-subtitle">Создавайте карточки водителей, привязывайте существующие карточки и управляйте списком.</p>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <Input label="Номер ТС" value={vehicleNumber} onChange={(event) => setVehicleNumber(event.target.value)} placeholder="Например, А123АА77" />
          <Input label="ФИО водителя (опционально)" value={driverName} onChange={(event) => setDriverName(event.target.value)} placeholder="Для создания аккаунта" />
          <Input label="Логин водителя (опционально)" value={driverLogin} onChange={(event) => setDriverLogin(event.target.value)} placeholder="Если нужен вход в систему" />
          <Input label="Пароль водителя (опционально)" type="password" value={driverPassword} onChange={(event) => setDriverPassword(event.target.value)} />
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          <Button onClick={() => void handleCreate()} loading={createMutation.isPending}>
            Создать карточку водителя
          </Button>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
          <Input
            label="Привязать существующего водителя по ID"
            value={attachDriverId}
            onChange={(event) => setAttachDriverId(event.target.value)}
            placeholder="ID водителя"
          />
          <Button variant="secondary" onClick={() => void handleAttach()} loading={attachMutation.isPending}>
            Привязать
          </Button>
        </div>

        {actionError ? <p className="mt-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{actionError}</p> : null}
      </article>

      {!data.length ? (
        <EmptyState title="Список водителей пуст" description="Создайте первую карточку водителя или привяжите существующую." />
      ) : (
        <article className="surface p-5">
          <Table
            data={data}
            rowKey={(item) => item.id}
            columns={[
              { key: 'id', title: 'ID', render: (item) => item.id },
              { key: 'vehicle', title: 'Номер ТС', render: (item) => item.vehicle_number },
              { key: 'name', title: 'ФИО', render: (item) => item.user_full_name ?? '—' },
              { key: 'login', title: 'Логин', render: (item) => item.user_login ?? '—' },
              {
                key: 'action',
                title: 'Действие',
                render: (item) => (
                  <Button variant="ghost" size="sm" onClick={() => void detachMutation.mutateAsync(item.id)} loading={detachMutation.isPending}>
                    Отвязать
                  </Button>
                ),
              },
            ]}
          />
        </article>
      )}
    </section>
  );
}
