import { Button } from '@/components/ui/Button';

type EmptyStateProps = {
  title: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
};

export function EmptyState({ title, description, actionText, onAction }: EmptyStateProps) {
  return (
    <div className="surface p-6 text-center">
      <h3 className="font-heading text-xl text-brand-900">{title}</h3>
      {description ? <p className="mt-2 text-sm text-brand-700">{description}</p> : null}
      {actionText && onAction ? (
        <div className="mt-4">
          <Button onClick={onAction}>{actionText}</Button>
        </div>
      ) : null}
    </div>
  );
}
