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
        <p className="font-sans text-xl font-semibold text-on-surface">
          {error ?? t('sites.not_found', 'Site introuvable')}
        </p>
        <button
          onClick={() => navigate('/sites')}
          className="text-sm text-primary font-sans hover:underline"
        >
          {t('sites.back_to_list', 'Retour a la liste')}
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-sans text-on-surface-variant">
        <button onClick={handleCancel} className="hover:text-on-surface transition-colors">
          {t('nav.sites')}
        </button>
        <span className="material-symbols-outlined text-sm">chevron_right</span>
        <span className="text-on-surface font-medium">{currentSite?.name}</span>
        <span className="material-symbols-outlined text-sm">chevron_right</span>
        <span className="text-on-surface font-medium">{t('common.edit', 'Modifier')}</span>
      </div>

      <div>
        <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight">
          {t('sites.edit_title', 'Modifier le site')}
        </h1>
        <p className="text-sm text-on-surface-variant font-sans mt-1">
          {currentSite?.name} &mdash; {currentSite?.code}
        </p>
      </div>

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
