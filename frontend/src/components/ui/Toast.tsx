import { useEffect } from 'react';

type ToastType = 'success' | 'error' | 'info';

interface ToastProps {
  message: string;
  type?: ToastType;
  isVisible: boolean;
  onClose: () => void;
  duration?: number;
}

const typeClasses: Record<ToastType, string> = {
  success: 'bg-secondary-container text-on-secondary-container',
  error: 'bg-error-container text-error',
  info: 'bg-surface-container text-on-surface',
};

export function Toast({
  message,
  type = 'info',
  isVisible,
  onClose,
  duration = 4000,
}: ToastProps) {
  useEffect(() => {
    if (!isVisible) return;
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [isVisible, onClose, duration]);

  if (!isVisible) return null;

  return (
    <div
      className={[
        'fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-md shadow-md px-4 py-3 font-sans text-sm',
        'animate-[slideUp_200ms_ease-out]',
        typeClasses[type],
      ].join(' ')}
      role="alert"
    >
      <span>{message}</span>
      <button
        type="button"
        onClick={onClose}
        className="ml-2 opacity-70 hover:opacity-100 transition-opacity cursor-pointer"
        aria-label="Dismiss"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </button>
    </div>
  );
}
