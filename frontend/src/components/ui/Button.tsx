import { forwardRef, type ButtonHTMLAttributes } from 'react';
import clsx from 'clsx';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  fullWidth?: boolean;
};

const variantClass: Record<ButtonVariant, string> = {
  primary: 'bg-brand-600 text-white shadow-md shadow-brand-600/30 hover:bg-brand-700 hover:shadow-brand-700/30 disabled:bg-brand-300',
  secondary: 'bg-accent-200 text-accent-900 shadow-sm hover:bg-accent-300 disabled:bg-accent-100',
  danger: 'bg-red-600 text-white shadow-md shadow-red-600/25 hover:bg-red-700 disabled:bg-red-300',
  ghost: 'bg-white/70 text-brand-700 hover:bg-brand-50 border border-brand-200 disabled:text-brand-300',
};

const sizeClass: Record<ButtonSize, string> = {
  sm: 'h-9 px-3 text-sm',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-5 text-base',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = 'primary', size = 'md', loading = false, fullWidth = false, children, disabled, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all duration-150 active:translate-y-px',
        variantClass[variant],
        sizeClass[size],
        fullWidth && 'w-full',
        className,
      )}
      {...props}
    >
      {loading ? 'Сохраняем...' : children}
    </button>
  );
});
