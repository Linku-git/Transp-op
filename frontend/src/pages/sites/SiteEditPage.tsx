import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSiteStore } from '@/stores/siteStore';
import { Skeleton } from '@/components/ui/Skeleton';
import { SiteForm } from './SiteForm';
import type { SiteCreate } from '@/types/site';
import type { AxiosError } from 'axios';
import type { ApiError } from '@/types';

export function SiteEditPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { currentSite, isLoading, error, fetchSite, updateSite } =
    useSiteStore();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchSite(id);
    }
  }, [id, fetchSite]);

  const handleSubmit = useCallback(
    async (data: SiteCreate) => {
      if (!id) return;
      setIsSubmitting(true);
      setApiError(null);
      try {
        await updateSite(id, data);
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
    [id, updateSite, navigate, t],
  );

  const handleCancel = useCallback(() => {
    navigate('/sites');
  }, [navigate]);

  /* Loading state */
  if (isLoading && !currentSite) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton variant="text" className="w-64 h-8" />
        <Skeleton variant="rectangular" className="w-full" height="400px" />
      </div>
    );
  }

  /* Not found / error state */
  if (!isLoading && !currentSite) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-2">
        <p className="font-display text-xl font-semibold text-on-surface">
          {error ?? t('sites.not_found', 'Site introuvable')}
        </p>
        <button
          onClick={() => navigate('/sites')}
          className="text-sm text-secondary font-sans hover:underline"
        >
          {t('sites.back_to_list', 'Retour a la liste')}
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-on-surface mb-8">
        {t('sites.edit_title', 'Modifier le site')}: {currentSite?.name}
      </h1>

      {currentSite && (
        <SiteForm
          initialData={currentSite}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
          apiError={apiError}
        />
      )}
    </div>
  );
}
