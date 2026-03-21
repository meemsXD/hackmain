import { Link } from 'react-router-dom';

export function ForbiddenPage() {
  return (
    <section className="surface p-6">
      <h1 className="page-title">Доступ ограничен</h1>
      <p className="page-subtitle">У вашей учетной записи нет прав для открытия этого раздела.</p>
      <div className="mt-4">
        <Link to="/app/profile" className="inline-flex h-10 items-center rounded-xl bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700">
          В профиль
        </Link>
      </div>
    </section>
  );
}
