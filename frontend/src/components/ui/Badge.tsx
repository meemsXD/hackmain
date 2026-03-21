import clsx from 'clsx';
import type { PropsWithChildren } from 'react';

type BadgeProps = PropsWithChildren<{
  tone?: 'neutral' | 'brand' | 'success' | 'warning' | 'danger';
}>;

const toneClass: Record<NonNullable<BadgeProps['tone']>, string> = {
  neutral: 'bg-slate-100 text-slate-700',
  brand: 'bg-brand-100 text-brand-800',
  success: 'bg-emerald-100 text-emerald-800',
  warning: 'bg-amber-100 text-amber-800',
  danger: 'bg-red-100 text-red-700',
};

export function Badge({ tone = 'neutral', children }: BadgeProps) {
  return <span className={clsx('inline-flex rounded-full px-2.5 py-1 text-xs font-semibold', toneClass[tone])}>{children}</span>;
}
