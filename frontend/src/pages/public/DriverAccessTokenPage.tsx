import { Link, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/Button';

export function DriverAccessTokenPage() {
  const { token } = useParams<{ token: string }>();

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <section className="surface w-full max-w-xl p-6">
        <h1 className="font-heading text-3xl text-brand-900">Доступ водителя по QR</h1>
        <p className="mt-2 text-sm text-brand-700">Код из ссылки можно вставить в разделе водителя для открытия партии.</p>
        <div className="mt-4 rounded-xl bg-brand-50 p-3 text-sm text-brand-900">
          <p className="font-semibold">Код:</p>
          <p className="mt-1 break-all">{token ?? 'Код не найден в ссылке'}</p>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link to="/login">
            <Button>Войти в систему</Button>
          </Link>
          <Link to="/app/driver/access">
            <Button variant="secondary">Перейти в экран доступа</Button>
          </Link>
        </div>
      </section>
    </main>
  );
}
