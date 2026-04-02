import { useCallback, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Button } from '@/components/ui/Button';
import { Toast } from '@/components/ui/Toast';

const EXPORT_FORMATS = ['CSV', 'Excel', 'PDF'] as const;

export function DAFExportButton() {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [toastVisible, setToastVisible] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleExport = useCallback((_format: string) => {
    setIsOpen(false);
    setToastVisible(true);
  }, []);

  const toggleMenu = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  return (
    <div className="relative inline-block" data-testid="daf-export-button">
      <Button variant="secondary" size="md" onClick={toggleMenu}>
        <span className="material-symbols-outlined mr-2 text-lg">download</span>
        {t('financial.export_daf', 'Export DAF')}
      </Button>

      {isOpen && (
        <div
          ref={menuRef}
          className="absolute right-0 mt-1 w-40 bg-surface-container-lowest rounded-lg shadow-lg border border-outline-variant/10 py-1 z-50"
        >
          {EXPORT_FORMATS.map((format) => (
            <button
              key={format}
              type="button"
              onClick={() => handleExport(format)}
              className="w-full text-left px-4 py-2 text-sm text-on-surface hover:bg-surface-container-low transition-colors"
            >
              {format}
            </button>
          ))}
        </div>
      )}

      <Toast
        message={t('financial.export_coming_soon', 'Export DAF bientot disponible')}
        type="info"
        isVisible={toastVisible}
        onClose={() => setToastVisible(false)}
      />
    </div>
  );
}
