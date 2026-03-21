import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { createBatch, listAllBatches } from '@/api/batches';
import { getApiErrorMessage } from '@/api/client';
import { Button, ErrorState, Input, Select } from '@/components/ui';

const schema = z.object({
  waste_type: z.string().min(2, 'Укажите тип отходов'),
  quantity: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Формат: 0.00'),
  medical_organization: z.string().min(1, 'Укажите id образовательной организации'),
  pickup_point: z.string().min(5, 'Укажите адрес вывоза'),
  delivery_point: z.string().min(1, 'Укажите id переработчика'),
});

type FormValues = z.infer<typeof schema>;

export function EducatorBatchNewPage() {
  const navigate = useNavigate();
  const [formError, setFormError] = useState('');

  const hintsQuery = useQuery({
    queryKey: ['batches', 'hints'],
    queryFn: () => listAllBatches(5),
  });

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      waste_type: '',
      quantity: '',
      medical_organization: '',
      pickup_point: '',
      delivery_point: '',
    },
  });

  const createMutation = useMutation({
    mutationFn: createBatch,
    onSuccess: (batch) => {
      navigate(`/app/educator/batches/${batch.id}`);
    },
  });

  const options = useMemo(() => {
    const source = hintsQuery.data ?? [];
    const medicalIds = [...new Set(source.map((item) => item.medical_organization))];
    const deliveryIds = [...new Set(source.map((item) => item.delivery_point))];
    return {
      medicalIds,
      deliveryIds,
    };
  }, [hintsQuery.data]);

  const onSubmit = form.handleSubmit(async (values) => {
    setFormError('');
    try {
      await createMutation.mutateAsync({
        waste_type: values.waste_type,
        quantity: values.quantity,
        medical_organization: Number(values.medical_organization),
        pickup_point: values.pickup_point,
        delivery_point: Number(values.delivery_point),
      });
    } catch (error) {
      setFormError(getApiErrorMessage(error));
    }
  });

  return (
    <section className="surface p-5">
      <h1 className="page-title">Создание партии</h1>
      <p className="page-subtitle">Форма валидируется на клиенте и отправляет данные напрямую в backend.</p>

      {hintsQuery.isError ? (
        <div className="mt-4">
          <ErrorState title="Не удалось загрузить подсказки" description="Можно заполнить id вручную и сохранить партию." />
        </div>
      ) : null}

      <form className="mt-5 grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
        <Input label="Тип отходов" error={form.formState.errors.waste_type?.message} {...form.register('waste_type')} />
        <Input label="Количество" error={form.formState.errors.quantity?.message} {...form.register('quantity')} />
        <div className="md:col-span-2">
          <Input label="Адрес вывоза" error={form.formState.errors.pickup_point?.message} {...form.register('pickup_point')} />
        </div>
        <div className="space-y-2">
          <Input
            label="ID образовательной организации"
            type="number"
            error={form.formState.errors.medical_organization?.message}
            {...form.register('medical_organization')}
          />
          <Select
            label="Подставить из существующих"
            placeholder="Не выбрано"
            options={options.medicalIds.map((id) => ({ value: String(id), label: `ID ${id}` }))}
            onChange={(event) => form.setValue('medical_organization', event.target.value)}
            value=""
          />
        </div>
        <div className="space-y-2">
          <Input label="ID переработчика" type="number" error={form.formState.errors.delivery_point?.message} {...form.register('delivery_point')} />
          <Select
            label="Подставить из существующих"
            placeholder="Не выбрано"
            options={options.deliveryIds.map((id) => ({ value: String(id), label: `ID ${id}` }))}
            onChange={(event) => form.setValue('delivery_point', event.target.value)}
            value=""
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
