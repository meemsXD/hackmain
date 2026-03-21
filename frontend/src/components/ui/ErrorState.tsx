import { Button } from '@/components/ui/Button';

type ErrorStateProps = {
  title?: string;
  description?: string;
  onRetry?: () => void;
};

export function ErrorState({
  title = 'Не удалось загрузить данные',
  description = 'Попробуйте обновить страницу или повторить запрос.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="surface border border-red-200 bg-red-50 p-5 text-red-800">
      <h3 className="font-semibold">{title}</h3>
      <p className="mt-1 text-sm">{description}</p>
      {onRetry ? (
        <div className="mt-4">
          <Button variant="danger" size="sm" onClick={onRetry}>
            Повторить
          </Button>
        </div>
      ) : null}
    </div>
  );
}
