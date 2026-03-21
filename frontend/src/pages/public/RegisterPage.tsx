import { useMemo, useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery } from '@tanstack/react-query';
import { listOrganizations } from '@/api/organizations';
import { getApiErrorMessage } from '@/api/client';
import { useAuth } from '@/auth/useAuth';
import { Input, Select, Button } from '@/components/ui';
import type { UserRole } from '@/app/constants/roles';
import { ROLE_LABELS } from '@/app/constants/roles';
import type { RegisterPayload } from '@/api/types';

const schema = z
  .object({
    full_name: z.string().min(3, 'Укажите ФИО'),
    login: z.string().min(3, 'Укажите логин'),
    password: z.string().min(6, 'Минимум 6 символов'),
    role: z.enum(['RECYCLER', 'DRIVER', 'MEDICAL', 'INSPECTOR', 'ADMIN']),
    organization: z.string().optional(),
    vehicle_number: z.string().optional(),
    license_number: z.string().optional(),
    address: z.string().optional(),
    facility_address: z.string().optional(),
  })
  .superRefine((value, ctx) => {
    if (value.role === 'RECYCLER') {
      if (!value.license_number?.trim()) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['license_number'], message: 'Нужен номер лицензии' });
      }
      if (!value.address?.trim()) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['address'], message: 'Нужен адрес организации' });
      }
    }
    if (value.role === 'MEDICAL') {
      if (!value.license_number?.trim()) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['license_number'], message: 'Нужен номер лицензии' });
      }
      if (!value.facility_address?.trim()) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['facility_address'], message: 'Нужен адрес площадки' });
      }
    }
  });

type FormValues = z.infer<typeof schema>;

const ROLE_OPTIONS: { value: UserRole; label: string }[] = [
  { value: 'RECYCLER', label: ROLE_LABELS.RECYCLER },
  { value: 'DRIVER', label: ROLE_LABELS.DRIVER },
  { value: 'MEDICAL', label: ROLE_LABELS.MEDICAL },
  { value: 'INSPECTOR', label: ROLE_LABELS.INSPECTOR },
  { value: 'ADMIN', label: ROLE_LABELS.ADMIN },
];

export function RegisterPage() {
  const navigate = useNavigate();
  const { status, register } = useAuth();
  const [formError, setFormError] = useState('');

  const organizationsQuery = useQuery({
    queryKey: ['organizations', 'register'],
    queryFn: () => listOrganizations(1),
  });

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      role: 'RECYCLER',
      full_name: '',
      login: '',
      password: '',
      organization: '',
      vehicle_number: '',
      license_number: '',
      address: '',
      facility_address: '',
    },
  });

  const role = form.watch('role');

  if (status === 'authenticated') {
    return <Navigate to="/app/profile" replace />;
  }

  const organizationOptions = useMemo(() => {
    const results = organizationsQuery.data?.results ?? [];
    return results.map((item) => ({ value: String(item.id), label: `${item.name} (${item.inn})` }));
  }, [organizationsQuery.data?.results]);

  const onSubmit = form.handleSubmit(async (values) => {
    setFormError('');
    try {
      const payload: RegisterPayload = {
        full_name: values.full_name.trim(),
        login: values.login.trim(),
        password: values.password,
        role: values.role,
        organization: values.organization ? Number(values.organization) : null,
      };

      if (values.role === 'RECYCLER') {
        if (values.license_number?.trim()) {
          payload.license_number = values.license_number.trim();
        }
        if (values.address?.trim()) {
          payload.address = values.address.trim();
        }
      }

      if (values.role === 'MEDICAL') {
        if (values.license_number?.trim()) {
          payload.license_number = values.license_number.trim();
        }
        if (values.facility_address?.trim()) {
          payload.facility_address = values.facility_address.trim();
        }
      }

      await register(payload);
      navigate('/app/profile', { replace: true });
    } catch (error) {
      setFormError(getApiErrorMessage(error));
    }
  });

  return (
    <main className="grid min-h-screen place-items-center px-4 py-8">
      <section className="surface w-full max-w-2xl animate-fade-in-up p-6">
        <h1 className="font-heading text-3xl text-brand-900">Регистрация</h1>
        <p className="mt-2 text-sm text-brand-700">Создайте аккаунт и выберите роль для работы в системе.</p>

        <form className="mt-5 grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
          <Input label="ФИО" error={form.formState.errors.full_name?.message} {...form.register('full_name')} />
          <Input label="Логин (email или username)" error={form.formState.errors.login?.message} {...form.register('login')} />
          <Input label="Пароль" type="password" error={form.formState.errors.password?.message} {...form.register('password')} />
          <Select label="Роль" options={ROLE_OPTIONS} error={form.formState.errors.role?.message} {...form.register('role')} />

          <div className="md:col-span-2">
            <Select
              label="Организация"
              placeholder="Выберите организацию (опционально)"
              options={organizationOptions}
              error={form.formState.errors.organization?.message}
              {...form.register('organization')}
            />
          </div>

          {role === 'DRIVER' ? (
            <div className="md:col-span-2">
              <Input
                label="Номер ТС (опционально)"
                hint="Временный обход: поле не отправляется на backend из-за ошибки модели водителя."
                error={form.formState.errors.vehicle_number?.message}
                {...form.register('vehicle_number')}
              />
            </div>
          ) : null}

          {role === 'RECYCLER' ? (
            <>
              <Input label="Номер лицензии" error={form.formState.errors.license_number?.message} {...form.register('license_number')} />
              <Input label="Адрес организации" error={form.formState.errors.address?.message} {...form.register('address')} />
            </>
          ) : null}

          {role === 'MEDICAL' ? (
            <>
              <Input label="Номер лицензии" error={form.formState.errors.license_number?.message} {...form.register('license_number')} />
              <Input label="Адрес площадки" error={form.formState.errors.facility_address?.message} {...form.register('facility_address')} />
            </>
          ) : null}

          {formError ? <p className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700 md:col-span-2">{formError}</p> : null}
          <div className="md:col-span-2">
            <Button fullWidth loading={form.formState.isSubmitting} type="submit">
              Создать аккаунт
            </Button>
          </div>
        </form>

        <p className="mt-4 text-sm text-brand-700">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="font-semibold text-brand-700 underline-offset-2 hover:underline">
            Войти
          </Link>
        </p>
      </section>
    </main>
  );
}
