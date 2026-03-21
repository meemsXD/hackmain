import { forwardRef, type SelectHTMLAttributes } from 'react';
import clsx from 'clsx';

type Option = {
  value: string | number;
  label: string;
};

type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
  error?: string;
  options: Option[];
  placeholder?: string;
};

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, error, options, placeholder, className, ...props },
  ref,
) {
  return (
    <label className="flex w-full flex-col gap-1.5">
      {label ? <span className="text-sm font-medium text-brand-900">{label}</span> : null}
      <select
        ref={ref}
        className={clsx(
          'h-10 w-full rounded-xl border border-brand-200 bg-white px-3 text-sm text-brand-900 outline-none ring-brand-300 transition focus:ring-2',
          error && 'border-red-400 focus:ring-red-200',
          className,
        )}
        {...props}
      >
        {placeholder ? <option value="">{placeholder}</option> : null}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </label>
  );
});
