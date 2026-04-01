import { type ReactNode } from 'react';

interface CardProps {
  title?: string;
  children: ReactNode;
  className?: string;
}

export function Card({ title, children, className = '' }: CardProps) {
  return (
    <div
      className={[
        'bg-surface-container-lowest rounded-lg p-6',
        className,
      ].join(' ')}
    >
      {title && (
        <h3 className="font-display text-lg font-semibold text-on-surface mb-4">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}
