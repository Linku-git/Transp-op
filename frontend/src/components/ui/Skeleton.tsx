type SkeletonVariant = 'text' | 'rectangular' | 'circular';

interface SkeletonProps {
  width?: string;
  height?: string;
  className?: string;
  variant?: SkeletonVariant;
}

const variantClasses: Record<SkeletonVariant, string> = {
  text: 'h-4 rounded',
  rectangular: 'rounded',
  circular: 'rounded-full',
};

export function Skeleton({
  width,
  height,
  className = '',
  variant = 'text',
}: SkeletonProps) {
  return (
    <div
      className={[
        'bg-surface-container-low/50 animate-pulse',
        variantClasses[variant],
        className,
      ].join(' ')}
      style={{
        width: width ?? undefined,
        height: variant !== 'text' ? height ?? undefined : undefined,
      }}
      aria-hidden="true"
    />
  );
}
