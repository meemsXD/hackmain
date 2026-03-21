import type { PropsWithChildren, ReactNode } from 'react';

type DrawerProps = PropsWithChildren<{
  open: boolean;
  onClose: () => void;
  title?: string;
  headerExtra?: ReactNode;
}>;

export function Drawer({ open, onClose, title, headerExtra, children }: DrawerProps) {
  return (
    <div
      className={`fixed inset-0 z-40 transition ${open ? 'pointer-events-auto bg-brand-950/40' : 'pointer-events-none bg-transparent'}`}
      onClick={onClose}
    >
      <aside
        className={`absolute right-0 top-0 h-full w-[88vw] max-w-sm bg-white p-4 shadow-2xl transition-transform ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between gap-3">
          <h3 className="font-heading text-xl text-brand-900">{title ?? 'Меню'}</h3>
          {headerExtra}
        </div>
        <div className="h-[calc(100%-3rem)] overflow-y-auto">{children}</div>
      </aside>
    </div>
  );
}
