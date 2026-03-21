import type { PropsWithChildren, ReactNode } from 'react';
import { Button } from '@/components/ui/Button';

type ModalProps = PropsWithChildren<{
  title: string;
  open: boolean;
  onClose: () => void;
  footer?: ReactNode;
}>;

export function Modal({ title, open, onClose, footer, children }: ModalProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 grid place-items-center bg-brand-900/40 p-4">
      <div className="w-full max-w-xl animate-fade-in-up rounded-2xl bg-white p-5 shadow-2xl">
        <div className="mb-4 flex items-start justify-between gap-4">
          <h3 className="font-heading text-xl text-brand-900">{title}</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            Закрыть
          </Button>
        </div>
        <div>{children}</div>
        {footer ? <div className="mt-4 border-t border-brand-100 pt-4">{footer}</div> : null}
      </div>
    </div>
  );
}
