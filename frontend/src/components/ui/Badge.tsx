import { type ReactNode } from 'react';

type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

interface BadgeProps {
  variant: BadgeVariant;
  children: ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: 'bg-secondary-container text-on-secondary-container',
  warning: 'bg-surface-container-high text-on-surface-variant',
  danger: 'bg-error-container text-error',
  info: 'bg-surface-container text-on-surface',
  neutral: 'bg-surface-container-high text-on-surface-variant',
};

export function Badge({ variant, children, className = '' }: BadgeProps) {
  return (
    <span
      className={[
        'inline-flex items-center text-xs font-medium px-2.5 py-0.5 rounded-full font-sans',
        variantClasses[variant],
        className,
      ].join(' ')}
    >
      {children}
    </span>
  );
}
