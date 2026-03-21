import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <main className="mx-auto grid min-h-screen max-w-xl place-items-center px-4">
      <div className="surface w-full p-6 text-center">
        <h1 className="font-heading text-3xl text-brand-900">Страница не найдена</h1>
        <p className="mt-2 text-sm text-brand-700">Проверьте ссылку или вернитесь в рабочий раздел.</p>
        <Link to="/app/profile" className="mt-4 inline-flex h-10 items-center rounded-xl bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700">
          Перейти в кабинет
        </Link>
      </div>
    </main>
  );
}
