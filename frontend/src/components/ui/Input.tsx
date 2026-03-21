import { forwardRef, type InputHTMLAttributes } from 'react';
import clsx from 'clsx';

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
  hint?: string;
};

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, hint, className, ...props },
  ref,
) {
  return (
    <label className="flex w-full flex-col gap-1.5">
      {label ? <span className="text-sm font-medium text-brand-900">{label}</span> : null}
      <input
        ref={ref}
        className={clsx(
          'h-10 w-full rounded-xl border border-brand-200 bg-white px-3 text-sm text-brand-900 outline-none ring-brand-300 transition focus:ring-2',
          error && 'border-red-400 focus:ring-red-200',
          className,
        )}
        {...props}
      />
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
      {!error && hint ? <span className="text-xs text-brand-600">{hint}</span> : null}
    </label>
  );
});
