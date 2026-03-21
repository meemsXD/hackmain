import { useMemo, useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@/auth/useAuth';
import { Input, Button } from '@/components/ui';
import { getApiErrorMessage } from '@/api/client';
import { getDefaultHomePath } from '@/utils/roles';

const schema = z.object({
  login: z.string().min(1, 'Введите логин или email'),
  password: z.string().min(1, 'Введите пароль'),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, status, roles } = useAuth();
  const [formError, setFormError] = useState('');

  const redirectTo = useMemo(() => {
    const from = location.state as { from?: string } | null;
    return from?.from || getDefaultHomePath(roles);
  }, [location.state, roles]);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      login: '',
      password: '',
    },
  });

  if (status === 'authenticated') {
    return <Navigate to={redirectTo} replace />;
  }

  const onSubmit = form.handleSubmit(async (values) => {
    setFormError('');
    try {
      await login(values);
      navigate(redirectTo, { replace: true });
    } catch (error) {
      setFormError(getApiErrorMessage(error));
    }
  });

  return (
    <main className="grid min-h-screen place-items-center px-4 py-8">
      <section className="surface w-full max-w-md animate-fade-in-up p-6">
        <h1 className="font-heading text-3xl text-brand-900">Вход в систему</h1>
        <p className="mt-2 text-sm text-brand-700">Введите учетные данные, чтобы продолжить работу.</p>

        <form onSubmit={onSubmit} className="mt-5 space-y-3">
          <Input label="Логин" placeholder="например, driver@example.com" error={form.formState.errors.login?.message} {...form.register('login')} />
          <Input
            label="Пароль"
            type="password"
            placeholder="Введите пароль"
            error={form.formState.errors.password?.message}
            {...form.register('password')}
          />
          {formError ? <p className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{formError}</p> : null}
          <Button fullWidth loading={form.formState.isSubmitting} type="submit">
            Войти
          </Button>
        </form>

        <p className="mt-4 text-sm text-brand-700">
          Нет аккаунта?{' '}
          <Link to="/register" className="font-semibold text-brand-700 underline-offset-2 hover:underline">
            Перейти к регистрации
          </Link>
        </p>
      </section>
    </main>
  );
}
