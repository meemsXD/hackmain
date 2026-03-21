import type { InputHTMLAttributes } from 'react';
import clsx from 'clsx';

type CheckboxProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
};

export function Checkbox({ label, className, ...props }: CheckboxProps) {
  return (
    <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-brand-900">
      <input type="checkbox" className={clsx('h-4 w-4 rounded border-brand-300 text-brand-600', className)} {...props} />
      <span>{label}</span>
    </label>
  );
}
