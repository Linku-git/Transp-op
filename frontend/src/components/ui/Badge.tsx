import { type ReactNode } from 'react';

type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

interface BadgeProps {
  variant: BadgeVariant;
  children: ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: 'bg-green-50 text-green-700',
  warning: 'bg-amber-50 text-amber-700',
  danger: 'bg-error-container/30 text-error',
  info: 'bg-primary/10 text-primary',
  neutral: 'bg-surface-container-high text-on-surface-variant',
};

export function Badge({ variant, children, className = '' }: BadgeProps) {
  return (
    <span
      className={[
        'inline-flex items-center text-[10px] font-bold uppercase tracking-wide px-2.5 py-0.5 rounded-full font-sans',
        variantClasses[variant],
        className,
      ].join(' ')}
    >
      {children}
    </span>
  );
}
