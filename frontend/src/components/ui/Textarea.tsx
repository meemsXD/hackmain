import { forwardRef, type TextareaHTMLAttributes } from 'react';
import clsx from 'clsx';

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string;
  error?: string;
};

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { label, error, className, ...props },
  ref,
) {
  return (
    <label className="flex w-full flex-col gap-1.5">
      {label ? <span className="text-sm font-medium text-brand-900">{label}</span> : null}
      <textarea
        ref={ref}
        className={clsx(
          'min-h-24 w-full rounded-xl border border-brand-200 bg-white px-3 py-2 text-sm text-brand-900 outline-none ring-brand-300 transition focus:ring-2',
          error && 'border-red-400 focus:ring-red-200',
          className,
        )}
        {...props}
      />
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </label>
  );
});
