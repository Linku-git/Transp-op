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
        'bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6',
        className,
      ].join(' ')}
    >
      {title && (
        <h3 className="font-sans text-sm font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}
