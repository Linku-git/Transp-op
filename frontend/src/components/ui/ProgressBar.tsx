type ProgressBarVariant = 'primary' | 'secondary' | 'error';

interface ProgressBarProps {
  value: number;
  label?: string;
  variant?: ProgressBarVariant;
}

const fillClasses: Record<ProgressBarVariant, string> = {
  primary: 'bg-primary',
  secondary: 'bg-primary',
  error: 'bg-error',
};

function clampValue(value: number): number {
  return Math.min(100, Math.max(0, value));
}

export function ProgressBar({
  value,
  label,
  variant = 'secondary',
}: ProgressBarProps) {
  const clamped = clampValue(value);
  const rounded = Math.round(clamped);

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-on-surface-variant font-sans">
            {label}
          </span>
          <span className="text-sm text-on-surface-variant font-sans tabular-nums">
            {rounded}%
          </span>
        </div>
      )}

      {!label && (
        <div className="flex justify-end">
          <span className="text-sm text-on-surface-variant font-sans tabular-nums">
            {rounded}%
          </span>
        </div>
      )}

      <div
        className="bg-surface-container-high rounded-full h-2 overflow-hidden"
        role="progressbar"
        aria-valuenow={rounded}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label ?? `${rounded}%`}
      >
        <div
          className={[
            'rounded-full h-2 transition-all duration-300',
            fillClasses[variant],
          ].join(' ')}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
