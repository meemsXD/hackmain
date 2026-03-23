import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { createBatch } from '@/api/batches';
import { getApiErrorMessage } from '@/api/client';
import { listAvailableRecyclers } from '@/api/users';
import { useAuth } from '@/auth/useAuth';
import { Button, EmptyState, ErrorState, Input, Select } from '@/components/ui';

const schema = z.object({
  waste_type: z.string().trim().min(1, 'Укажите тип отходов'),
  quantity: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Формат: 0.00'),
  medical_organization: z.string().min(1, 'Профиль образователя не найден'),
  pickup_point: z.string().min(5, 'Укажите адрес вывоза'),
  delivery_point: z.string().min(1, 'Выберите переработчика'),
  qr_expires_hours: z
    .string()
    .regex(/^\d+$/, 'Укажите число')
    .refine((value) => {
      const hours = Number(value);
      return Number.isInteger(hours) && hours >= 1 && hours <= 168;
    }, 'От 1 до 168 часов'),
});

type FormValues = z.infer<typeof schema>;

export function EducatorBatchNewPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [formError, setFormError] = useState('');

  const recyclersQuery = useQuery({
    queryKey: ['recyclers', 'available', 'educator'],
    queryFn: listAvailableRecyclers,
  });

  const medicalOrgId = user?.educator_profile?.id ? String(user.educator_profile.id) : '';

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      waste_type: '',
      quantity: '',
      medical_organization: medicalOrgId,
      pickup_point: '',
      delivery_point: '',
      qr_expires_hours: '24',
    },
  });

  useEffect(() => {
    if (medicalOrgId) {
      form.setValue('medical_organization', medicalOrgId, { shouldValidate: true });
    }
  }, [form, medicalOrgId]);

  const recyclerOptions = useMemo(() => {
    return (recyclersQuery.data ?? []).map((item) => ({
      value: String(item.id),
      label: `ID ${item.id} · ${item.license_number} · ${item.facility_address}`,
    }));
  }, [recyclersQuery.data]);

  useEffect(() => {
    if (recyclerOptions.length === 1 && !form.getValues('delivery_point')) {
      form.setValue('delivery_point', recyclerOptions[0].value, { shouldValidate: true });
    }
  }, [form, recyclerOptions]);

  const createMutation = useMutation({
    mutationFn: createBatch,
    onSuccess: (batch) => {
      navigate(`/app/educator/batches/${batch.id}`);
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setFormError('');
    try {
      await createMutation.mutateAsync({
        waste_type: values.waste_type.trim(),
        quantity: values.quantity,
        medical_organization: Number(medicalOrgId || values.medical_organization),
        pickup_point: values.pickup_point.trim(),
        delivery_point: Number(values.delivery_point),
        qr_expires_hours: Number(values.qr_expires_hours),
      });
    } catch (error) {
      setFormError(getApiErrorMessage(error));
    }
  });

  if (!medicalOrgId) {
    return (
      <EmptyState
        title="Профиль образователя не настроен"
        description="Для создания партии в аккаунте должен быть заполнен профиль образователя (лицензия и адрес)."
      />
    );
  }

  return (
    <section className="surface p-5">
      <h1 className="page-title">Создание партии</h1>
      <p className="page-subtitle">При создании партии автоматически формируется QR-токен с выбранным сроком действия.</p>

      {recyclersQuery.isError ? (
        <div className="mt-4">
          <ErrorState
            title="Не удалось загрузить переработчиков"
            description="Можно ввести ID переработчика вручную, но лучше обновить страницу и проверить доступы вашей организации."
          />
        </div>
      ) : null}

      <form className="mt-5 grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
        <Input label="Тип отходов" error={form.formState.errors.waste_type?.message} {...form.register('waste_type')} />
        <Input label="Количество" error={form.formState.errors.quantity?.message} {...form.register('quantity')} />

        <div className="md:col-span-2">
          <Input label="Адрес вывоза" error={form.formState.errors.pickup_point?.message} {...form.register('pickup_point')} />
        </div>

        <Input label="ID вашей образовательной организации" value={medicalOrgId} readOnly />

        <div className="space-y-2">
          <Input label="ID переработчика" type="number" error={form.formState.errors.delivery_point?.message} {...form.register('delivery_point')} />
          <Select
            label="Выбрать из доступных"
            placeholder="Не выбрано"
            options={recyclerOptions}
            onChange={(event) => form.setValue('delivery_point', event.target.value, { shouldValidate: true })}
            value={form.watch('delivery_point') || ''}
          />
          <p className="text-xs text-brand-700">Показываются переработчики, доступные в рамках вашей организации.</p>
        </div>

        <div className="md:col-span-2">
          <Input
            label="Срок действия QR (часы, 1-168)"
            type="number"
            error={form.formState.errors.qr_expires_hours?.message}
            {...form.register('qr_expires_hours')}
          />
        </div>

        {formError ? <p className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700 md:col-span-2">{formError}</p> : null}
        <div className="md:col-span-2">
          <Button type="submit" loading={createMutation.isPending}>
            Создать партию
          </Button>
        </div>
      </form>
    </section>
  );
}

