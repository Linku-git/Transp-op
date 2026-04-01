import { useCallback, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import L from 'leaflet';
import { useSiteStore } from '@/stores/siteStore';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import type { SecurityProfile } from '@/types/site';
import 'leaflet/dist/leaflet.css';

/* Fix default marker icons */
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
});

function InfoRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs font-medium text-on-surface-variant font-sans uppercase tracking-wide">
        {label}
      </span>
      <span className="text-sm text-on-surface font-sans">
        {value ?? '\u2014'}
      </span>
    </div>
  );
}

function SecurityChip({ profile }: { profile: SecurityProfile }) {
  const { t } = useTranslation();

  const labelMap: Record<SecurityProfile, string> = {
    normal: t('sites.security.normal', 'Normal'),
    elevated: t('sites.security.elevated', 'Eleve'),
    critical: t('sites.security.critical', 'Critique'),
  };

  const classMap: Record<SecurityProfile, string> = {
    normal: 'bg-surface-container text-on-surface-variant',
    elevated: 'bg-secondary-container text-on-secondary-container',
    critical: 'bg-error-container text-error',
  };

  return (
    <span
      className={[
        'inline-block rounded-md px-2.5 py-1 text-xs font-sans font-medium',
        classMap[profile],
      ].join(' ')}
    >
      {labelMap[profile]}
    </span>
  );
}

function SummaryCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="bg-surface-container rounded-lg p-4">
      <p className="text-xs font-medium text-on-surface-variant font-sans mb-1">
        {label}
      </p>
      <span className="font-display text-2xl font-bold text-secondary tabular-nums">
        {value}
      </span>
    </div>
  );
}

function formatTime(time: string | null | undefined): string {
  if (!time) return '\u2014';
  return time;
}

export function SiteDetailPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { currentSite, isLoading, error, fetchSite, deleteSite } =
    useSiteStore();

  useEffect(() => {
    if (id) {
      fetchSite(id);
    }
  }, [id, fetchSite]);

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
        <p className="font-display text-xl font-semibold text-on-surface">
          {error ?? t('sites.not_found', 'Site introuvable')}
        </p>
        <Link
          to="/sites"
          className="text-sm text-secondary font-sans hover:underline"
        >
          {t('sites.back_to_list', 'Retour a la liste')}
        </Link>
      </div>
    );
  }

  if (!currentSite) return null;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <h1 className="font-display text-2xl font-bold text-on-surface">
            {currentSite.name}
          </h1>
          <span className="text-sm text-on-surface-variant font-sans">
            {currentSite.code}
          </span>
          {currentSite.zfe_zone && (
            <span className="inline-block rounded-md bg-secondary-container text-on-secondary-container px-2 py-0.5 text-xs font-sans font-medium">
              ZFE
            </span>
          )}
          <SecurityChip profile={currentSite.security_profile} />
        </div>
        <div className="flex items-center gap-2">
          <Link to={`/sites/${currentSite.id}/edit`}>
            <Button variant="secondary">{t('common.edit')}</Button>
          </Link>
          <Button variant="danger" onClick={handleDelete}>
            {t('common.delete')}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Site Information */}
        <Card title={t('sites.detail.info', 'Informations')}>
          <div className="grid grid-cols-2 gap-x-6 gap-y-4">
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
          <div className="rounded-lg overflow-hidden" style={{ height: '280px' }}>
            <MapContainer
              center={[currentSite.lat, currentSite.lng]}
              zoom={14}
              style={{ height: '100%', width: '100%' }}
              scrollWheelZoom={false}
              dragging={false}
              zoomControl={false}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={[currentSite.lat, currentSite.lng]} />
            </MapContainer>
          </div>
        </Card>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <SummaryCard
          label={t('sites.detail.employee_count', 'Employes')}
          value={0}
        />
        <SummaryCard
          label={t('sites.detail.vehicle_count', 'Vehicules')}
          value={0}
        />
        <SummaryCard
          label={t('sites.detail.pmr_count', 'PMR')}
          value={0}
        />
      </div>

      {/* Shift schedule */}
      <Card title={t('sites.detail.shifts', 'Horaires des equipes')}>
        <div className="flex flex-col gap-3">
          {Array.from({ length: currentSite.num_shifts }, (_, i) => {
            const n = i + 1;
            const entry =
              n === 1
                ? currentSite.shift_1_entry
                : n === 2
                  ? currentSite.shift_2_entry
                  : currentSite.shift_3_entry;
            const exit =
              n === 1
                ? currentSite.shift_1_exit
                : n === 2
                  ? currentSite.shift_2_exit
                  : currentSite.shift_3_exit;
            return (
              <div
                key={n}
                className="flex items-center gap-4 bg-surface-container rounded-lg px-4 py-3"
              >
                <span className="text-sm font-medium text-on-surface font-sans w-24">
                  {t('sites.form.shift_n', 'Equipe {{n}}', { n })}
                </span>
                <span className="text-sm text-on-surface-variant font-sans tabular-nums">
                  {formatTime(entry)} &mdash; {formatTime(exit)}
                </span>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Notes */}
      {(currentSite.access_notes || currentSite.parking_notes || currentSite.observations) && (
        <div className="mt-6">
          <Card title={t('sites.form.section_notes', 'Notes')}>
            <div className="flex flex-col gap-4">
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
        </div>
      )}
    </div>
  );
}
