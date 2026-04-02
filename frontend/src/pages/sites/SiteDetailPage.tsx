import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSiteStore } from '@/stores/siteStore';
import { getSiteSummary } from '@/api/sites';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/Skeleton';
import { SiteSummaryCards } from '@/components/sites/SiteSummaryCards';
import { ShiftConfigPanel } from '@/components/sites/ShiftConfigPanel';
import { MapView } from '@/components/maps/MapView';
import { SiteMarker } from '@/components/maps/SiteMarker';
import type { SecurityProfile, SiteSummary } from '@/types/site';

function InfoRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] font-bold text-on-surface-variant font-sans uppercase tracking-widest">
        {label}
      </span>
      <span className="text-sm text-on-surface font-sans">
        {value ?? '\u2014'}
      </span>
    </div>
  );
}

const securityBadgeVariant: Record<SecurityProfile, 'success' | 'warning' | 'danger'> = {
  normal: 'success',
  elevated: 'warning',
  critical: 'danger',
};

export function SiteDetailPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { currentSite, isLoading, error, fetchSite, deleteSite } =
    useSiteStore();

  const [summary, setSummary] = useState<SiteSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  useEffect(() => {
    if (id) {
      fetchSite(id);
    }
  }, [id, fetchSite]);

  /* Fetch summary data independently from the store */
  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setSummaryLoading(true);
    getSiteSummary(id)
      .then((data) => {
        if (!cancelled) {
          setSummary(data);
        }
      })
      .catch(() => {
        /* Summary failure is non-critical; leave as null */
      })
      .finally(() => {
        if (!cancelled) {
          setSummaryLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const handleDelete = useCallback(async () => {
    if (!currentSite) return;
    const confirmed = window.confirm(
      t('sites.delete_confirm', 'Supprimer le site "{{name}}" ?', {
        name: currentSite.name,
      }),
    );
    if (confirmed) {
      await deleteSite(currentSite.id);
      navigate('/sites');
    }
  }, [currentSite, deleteSite, navigate, t]);

  /* Loading state */
  if (isLoading && !currentSite) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton variant="text" className="w-64 h-8" />
        <div className="grid grid-cols-3 gap-4">
          <Skeleton variant="rectangular" className="w-full" height="80px" />
          <Skeleton variant="rectangular" className="w-full" height="80px" />
          <Skeleton variant="rectangular" className="w-full" height="80px" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton variant="rectangular" className="w-full" height="300px" />
          <Skeleton variant="rectangular" className="w-full" height="300px" />
        </div>
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
        <Link
          to="/sites"
          className="text-sm text-primary font-sans hover:underline"
        >
          {t('sites.back_to_list', 'Retour a la liste')}
        </Link>
      </div>
    );
  }

  if (!currentSite) return null;

  const hasNotes =
    currentSite.access_notes || currentSite.parking_notes || currentSite.observations;

  const securityLabel: Record<SecurityProfile, string> = {
    normal: t('sites.security.normal', 'Normal'),
    elevated: t('sites.security.elevated', 'Eleve'),
    critical: t('sites.security.critical', 'Critique'),
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-sans text-on-surface-variant">
        <Link to="/sites" className="hover:text-on-surface transition-colors">
          {t('nav.sites')}
        </Link>
        <span className="material-symbols-outlined text-sm">chevron_right</span>
        <span className="text-on-surface font-medium">{currentSite.name}</span>
      </div>

      {/* Header */}
      <div className="flex items-end justify-between">
        <div className="flex items-center gap-4 flex-wrap">
          <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight">
            {currentSite.name}
          </h1>
          <span className="font-mono text-sm text-on-surface-variant bg-surface-container-low rounded-lg px-2.5 py-1">
            {currentSite.code}
          </span>
          {currentSite.zfe_zone && (
            <Badge variant="success">ZFE</Badge>
          )}
          <Badge variant={securityBadgeVariant[currentSite.security_profile]}>
            {securityLabel[currentSite.security_profile]}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Link to={`/sites/${currentSite.id}/edit`}>
            <Button variant="secondary">
              <span className="material-symbols-outlined text-base mr-1.5">edit</span>
              {t('common.edit', 'Modifier')}
            </Button>
          </Link>
          <Button variant="danger" onClick={handleDelete}>
            <span className="material-symbols-outlined text-base mr-1.5">delete</span>
            {t('common.delete', 'Supprimer')}
          </Button>
        </div>
      </div>

      {/* Summary stats */}
      <SiteSummaryCards
        summary={
          summary ?? { employee_count: 0, vehicle_count: 0, pmr_count: 0 }
        }
        isLoading={summaryLoading}
      />

      {/* Info grid + Mini-map */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title={t('sites.detail.info', 'Informations')}>
          <div className="grid grid-cols-2 gap-x-6 gap-y-5">
            <InfoRow label={t('sites.form.code', 'Code')} value={currentSite.code} />
            <InfoRow label={t('sites.form.name', 'Nom')} value={currentSite.name} />
            <InfoRow label={t('sites.form.address', 'Adresse')} value={currentSite.address} />
            <InfoRow label={t('sites.form.city', 'Ville')} value={currentSite.city} />
            <InfoRow
              label={t('sites.form.lat', 'Latitude')}
              value={currentSite.lat.toFixed(6)}
            />
            <InfoRow
              label={t('sites.form.lng', 'Longitude')}
              value={currentSite.lng.toFixed(6)}
            />
            <InfoRow
              label={t('sites.form.working_days', 'Jours travailles')}
              value={currentSite.working_days}
            />
            <InfoRow
              label={t('sites.form.days_per_week', 'Jours/semaine')}
              value={currentSite.days_per_week}
            />
            <InfoRow
              label={t('sites.form.contact_name', 'Contact')}
              value={currentSite.contact_name}
            />
            <InfoRow
              label={t('sites.form.contact_phone', 'Telephone')}
              value={currentSite.contact_phone}
            />
          </div>
        </Card>

        {/* Mini-map */}
        <Card title={t('sites.detail.location', 'Localisation')}>
          <div className="rounded-xl overflow-hidden" style={{ height: '300px' }}>
            <MapView
              center={[currentSite.lat, currentSite.lng]}
              zoom={14}
              height="300px"
            >
              <SiteMarker site={currentSite} />
            </MapView>
          </div>
        </Card>
      </div>

      {/* Shift schedule */}
      <Card>
        <ShiftConfigPanel site={currentSite} />
      </Card>

      {/* Quick action links */}
      <div className="flex items-center gap-3">
        <Link to={`/employees?site_id=${currentSite.id}`}>
          <Button variant="secondary">
            <span className="material-symbols-outlined text-base mr-1.5">groups</span>
            {t('sites.detail.view_employees', 'Voir les employes')}
          </Button>
        </Link>
        <Link to={`/vehicles?site_id=${currentSite.id}`}>
          <Button variant="secondary">
            <span className="material-symbols-outlined text-base mr-1.5">directions_bus</span>
            {t('sites.detail.view_vehicles', 'Voir les vehicules')}
          </Button>
        </Link>
      </div>

      {/* Notes */}
      {hasNotes && (
        <Card title={t('sites.form.section_notes', 'Notes')}>
          <div className="flex flex-col gap-5">
            {currentSite.access_notes && (
              <InfoRow
                label={t('sites.form.access_notes', "Notes d'acces")}
                value={currentSite.access_notes}
              />
            )}
            {currentSite.parking_notes && (
              <InfoRow
                label={t('sites.form.parking_notes', 'Notes de parking')}
                value={currentSite.parking_notes}
              />
            )}
            {currentSite.observations && (
              <InfoRow
                label={t('sites.form.observations', 'Observations')}
                value={currentSite.observations}
              />
            )}
          </div>
        </Card>
      )}

      {/* Bottom actions */}
      <div className="flex items-center gap-3">
        <Link to={`/sites/${currentSite.id}/edit`}>
          <Button variant="secondary">
            <span className="material-symbols-outlined text-base mr-1.5">edit</span>
            {t('common.edit', 'Modifier')}
          </Button>
        </Link>
        <Button variant="danger" onClick={handleDelete}>
          <span className="material-symbols-outlined text-base mr-1.5">delete</span>
          {t('common.delete', 'Supprimer')}
        </Button>
        <Link to="/sites" className="ml-auto">
          <Button variant="ghost">
            <span className="material-symbols-outlined text-base mr-1.5">arrow_back</span>
            {t('sites.back_to_list', 'Retour a la liste')}
          </Button>
        </Link>
      </div>
    </div>
  );
}
