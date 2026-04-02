import { type InputHTMLAttributes, forwardRef, useId } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  function Input({ label, error, className = '', id: externalId, type = 'text', ...rest }, ref) {
    const generatedId = useId();
    const inputId = externalId ?? generatedId;

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          type={type}
          className={[
            'w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm',
            'placeholder:text-on-surface-variant/60',
            'outline-none transition-shadow duration-150',
            error
              ? 'ring-2 ring-error/40'
              : 'focus:ring-2 focus:ring-primary/20',
            className,
          ].join(' ')}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? `${inputId}-error` : undefined}
          {...rest}
        />
        {error && (
          <p id={`${inputId}-error`} className="text-sm text-error font-sans" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  },
);
