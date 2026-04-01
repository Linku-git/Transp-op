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
    <div>
      <h1 className="font-display text-2xl font-bold text-on-surface mb-8">
        {t('sites.create_title', 'Nouveau site')}
      </h1>

      <SiteForm
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={isSubmitting}
        apiError={apiError}
      />
    </div>
  );
}
