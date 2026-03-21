import { Button } from '@/components/ui/Button';

type PaginationProps = {
  page: number;
  total: number;
  pageSize?: number;
  onPageChange: (page: number) => void;
};

export function Pagination({ page, total, pageSize = 20, onPageChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="flex items-center justify-between gap-3">
      <p className="text-sm text-brand-700">
        Страница {page} из {totalPages}
      </p>
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          Назад
        </Button>
        <Button variant="ghost" size="sm" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
          Вперед
        </Button>
      </div>
    </div>
  );
}
