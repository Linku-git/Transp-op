import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSiteStore } from '@/stores/siteStore';
import { SiteForm } from './SiteForm';
import type { SiteCreate } from '@/types/site';
import type { AxiosError } from 'axios';
import type { ApiError } from '@/types';

export function SiteCreatePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { createSite } = useSiteStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (data: SiteCreate) => {
      setIsSubmitting(true);
      setApiError(null);
      try {
        await createSite(data);
        navigate('/sites');
      } catch (err: unknown) {
        const axiosErr = err as AxiosError<ApiError>;
        setApiError(
          axiosErr.response?.data?.detail ?? t('common.error'),
        );
      } finally {
        setIsSubmitting(false);
      }
    },
    [createSite, navigate, t],
  );

  const handleCancel = useCallback(() => {
    navigate('/sites');
  }, [navigate]);

  return (
    <div className="flex flex-col gap-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-sans text-on-surface-variant">
        <button onClick={handleCancel} className="hover:text-on-surface transition-colors">
          {t('nav.sites')}
        </button>
        <span className="material-symbols-outlined text-sm">chevron_right</span>
        <span className="text-on-surface font-medium">{t('sites.create_title', 'Nouveau site')}</span>
      </div>

      <div>
        <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight">
          {t('sites.create_title', 'Nouveau site')}
        </h1>
        <p className="text-sm text-on-surface-variant font-sans mt-1">
          {t('sites.create_description', 'Remplissez les informations du nouveau site industriel')}
        </p>
      </div>

      <SiteForm
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={isSubmitting}
        apiError={apiError}
      />
    </div>
  );
}
