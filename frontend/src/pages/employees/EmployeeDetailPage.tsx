import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { useEmployeeStore } from '@/stores/employeeStore';
import { getSite } from '@/api/sites';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/Skeleton';
import type { Site } from '@/types/site';
import type { OptInChoice } from '@/types/employee';
import 'leaflet/dist/leaflet.css';

function InfoRow({
  label,
  value,
}: {
  label: string;
  value: string | number | null | undefined;
}) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[10px] font-bold text-on-surface-variant font-sans uppercase tracking-widest">
        {label}
      </span>
      <span className="text-sm text-on-surface font-sans">
        {value ?? '\u2014'}
      </span>
    </div>
  );
}

const optInBadgeVariant: Record<OptInChoice, 'success' | 'neutral' | 'warning'> = {
  Oui: 'success',
  Non: 'neutral',
  'Sous conditions': 'warning',
};

export function EmployeeDetailPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const {
    currentEmployee,
    isLoading,
    error,
    fetchEmployee,
    deleteEmployee,
  } = useEmployeeStore();

  const [site, setSite] = useState<Site | null>(null);
  const [siteLoading, setSiteLoading] = useState(false);

  useEffect(() => {
    if (id) {
      fetchEmployee(id);
    }
  }, [id, fetchEmployee]);

  /* Fetch site data for the mini-map */
  useEffect(() => {
    if (!currentEmployee?.site_id) return;
    let cancelled = false;
    setSiteLoading(true);
    getSite(currentEmployee.site_id)
      .then((data) => {
        if (!cancelled) {
          setSite(data);
        }
      })
      .catch(() => {
        /* Site fetch failure is non-critical */
      })
      .finally(() => {
        if (!cancelled) {
          setSiteLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [currentEmployee?.site_id]);

  const handleDelete = useCallback(async () => {
    if (!currentEmployee) return;
    const name = `${currentEmployee.first_name} ${currentEmployee.last_name}`;
    const confirmed = window.confirm(
      t('employees.delete_confirm', 'Supprimer l\'employe "{{name}}" ?', {
        name,
      }),
    );
    if (confirmed) {
      await deleteEmployee(currentEmployee.id);
      navigate('/employees');
    }
  }, [currentEmployee, deleteEmployee, navigate, t]);

  /* Loading state */
  if (isLoading && !currentEmployee) {
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
  if (!isLoading && !currentEmployee) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-2">
        <p className="font-sans text-xl font-semibold text-on-surface">
          {error ?? t('employees.not_found', 'Employe introuvable')}
        </p>
        <Link
          to="/employees"
          className="text-sm text-primary font-sans hover:underline"
        >
          {t('employees.back_to_list', 'Retour a la liste')}
        </Link>
      </div>
    );
  }

  if (!currentEmployee) return null;

  const fullName = `${currentEmployee.first_name} ${currentEmployee.last_name}`;
  const hasLocation =
    currentEmployee.lat !== null && currentEmployee.lng !== null;
  const hasSiteLocation = site !== null && !siteLoading;

  /* Calculate map center and bounds based on available markers */
  const mapCenter: [number, number] = hasLocation
    ? [currentEmployee.lat as number, currentEmployee.lng as number]
    : hasSiteLocation
      ? [site.lat, site.lng]
      : [33.57, -7.59];

  const mapZoom =
    hasLocation && hasSiteLocation ? 12 : 14;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3 flex-wrap">
          <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight">
            {fullName}
          </h1>
          <span className="text-sm text-on-surface-variant font-sans">
            {currentEmployee.matricule}
          </span>
          {currentEmployee.is_pmr && (
            <Badge variant="success">PMR</Badge>
          )}
          <Badge variant={currentEmployee.active ? 'success' : 'danger'}>
            {currentEmployee.active
              ? t('employees.badges.active', 'Actif')
              : t('employees.badges.inactive', 'Inactif')}
          </Badge>
          <Badge
            variant={
              optInBadgeVariant[currentEmployee.opt_in_company_transport]
            }
          >
            {t('employees.badges.opt_in_label', 'Opt-in')}:{' '}
            {currentEmployee.opt_in_company_transport}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Link to={`/employees/${currentEmployee.id}/edit`}>
            <Button variant="secondary">{t('common.edit', 'Modifier')}</Button>
          </Link>
          <Button variant="danger" onClick={handleDelete}>
            {t('common.delete', 'Supprimer')}
          </Button>
        </div>
      </div>

      {/* Info grid + Mini-map */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Main info */}
        <Card title={t('employees.detail.info', 'Informations')}>
          <div className="grid grid-cols-2 gap-x-6 gap-y-4">
            <InfoRow
              label={t('employees.form.matricule', 'Matricule')}
              value={currentEmployee.matricule}
            />
            <InfoRow
              label={t('employees.detail.site', 'Site')}
              value={currentEmployee.site_name}
            />
            <InfoRow
              label={t('employees.form.shift_time', 'Equipe')}
              value={currentEmployee.shift_time}
            />
            <InfoRow
              label={t('employees.form.department', 'Departement')}
              value={currentEmployee.department}
            />
            <InfoRow
              label={t('employees.form.phone', 'Telephone')}
              value={currentEmployee.phone}
            />
            <InfoRow
              label={t('employees.form.function_role', 'Fonction')}
              value={currentEmployee.function_role}
            />
          </div>
        </Card>

        {/* Mini-map with employee home + site location */}
        <Card title={t('employees.detail.location_map', 'Carte')}>
          <div
            className="rounded-lg overflow-hidden"
            style={{ height: '280px' }}
          >
            {(hasLocation || hasSiteLocation) ? (
              <MapContainer
                center={mapCenter}
                zoom={mapZoom}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={false}
                dragging={false}
                zoomControl={false}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {/* Employee home marker - primary blue */}
                {hasLocation && (
                  <CircleMarker
                    center={[
                      currentEmployee.lat as number,
                      currentEmployee.lng as number,
                    ]}
                    radius={8}
                    pathOptions={{
                      fillColor: '#0058be',
                      fillOpacity: 0.9,
                      color: '#003d82',
                      weight: 2,
                    }}
                  >
                    <Popup>
                      <span className="text-sm font-sans">
                        {fullName}
                        <br />
                        {currentEmployee.address ?? t('employees.detail.home', 'Domicile')}
                      </span>
                    </Popup>
                  </CircleMarker>
                )}
                {/* Site marker - secondary navy */}
                {hasSiteLocation && (
                  <CircleMarker
                    center={[site.lat, site.lng]}
                    radius={10}
                    pathOptions={{
                      fillColor: '#495e8a',
                      fillOpacity: 0.9,
                      color: '#323f5e',
                      weight: 2,
                    }}
                  >
                    <Popup>
                      <span className="text-sm font-sans">
                        {site.name}
                        <br />
                        {site.address}
                      </span>
                    </Popup>
                  </CircleMarker>
                )}
              </MapContainer>
            ) : (
              <div className="flex items-center justify-center h-full bg-surface-container rounded-lg">
                <p className="text-sm text-on-surface-variant font-sans">
                  {t(
                    'employees.detail.no_location',
                    'Aucune coordonnee disponible',
                  )}
                </p>
              </div>
            )}
          </div>
          {(hasLocation || hasSiteLocation) && (
            <div className="flex items-center gap-6 mt-3">
              {hasLocation && (
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block w-3 h-3 rounded-full"
                    style={{ backgroundColor: '#0058be' }}
                  />
                  <span className="text-xs text-on-surface-variant font-sans">
                    {t('employees.detail.home', 'Domicile')}
                  </span>
                </div>
              )}
              {hasSiteLocation && (
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block w-3 h-3 rounded-full"
                    style={{ backgroundColor: '#495e8a' }}
                  />
                  <span className="text-xs text-on-surface-variant font-sans">
                    {t('employees.detail.site_marker', 'Site')}
                  </span>
                </div>
              )}
            </div>
          )}
        </Card>
      </div>

      {/* Transport profile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card
          title={t(
            'employees.detail.transport_profile',
            'Profil de transport',
          )}
        >
          <div className="grid grid-cols-2 gap-x-6 gap-y-4">
            <InfoRow
              label={t(
                'employees.form.current_transport_mode',
                'Mode actuel',
              )}
              value={currentEmployee.current_transport_mode}
            />
            <InfoRow
              label={t(
                'employees.form.opt_in_company_transport',
                'Opt-in entreprise',
              )}
              value={currentEmployee.opt_in_company_transport}
            />
            <InfoRow
              label={t('employees.form.has_private_car', 'Vehicule personnel')}
              value={
                currentEmployee.has_private_car
                  ? t('common.yes', 'Oui')
                  : t('common.no', 'Non')
              }
            />
            <InfoRow
              label={t(
                'employees.form.volunteer_driver',
                'Conducteur volontaire',
              )}
              value={
                currentEmployee.volunteer_driver
                  ? t('common.yes', 'Oui')
                  : t('common.no', 'Non')
              }
            />
            {currentEmployee.volunteer_driver && (
              <InfoRow
                label={t(
                  'employees.form.carpool_seats',
                  'Places covoiturage',
                )}
                value={currentEmployee.carpool_seats}
              />
            )}
            <InfoRow
              label={t(
                'employees.form.transport_required',
                'Transport requis',
              )}
              value={
                currentEmployee.transport_required
                  ? t('common.yes', 'Oui')
                  : t('common.no', 'Non')
              }
            />
            <InfoRow
              label={t('employees.form.is_pmr', 'PMR')}
              value={
                currentEmployee.is_pmr
                  ? t('common.yes', 'Oui')
                  : t('common.no', 'Non')
              }
            />
          </div>
        </Card>

        {/* Address card */}
        <Card title={t('employees.detail.address_info', 'Adresse')}>
          <div className="grid grid-cols-2 gap-x-6 gap-y-4">
            <InfoRow
              label={t('employees.form.address', 'Adresse')}
              value={currentEmployee.address}
            />
            <InfoRow
              label={t('employees.form.quartier', 'Quartier')}
              value={currentEmployee.quartier}
            />
            <InfoRow
              label={t('employees.form.city', 'Ville')}
              value={currentEmployee.city}
            />
            <div />
            <InfoRow
              label={t('employees.form.lat', 'Latitude')}
              value={
                currentEmployee.lat !== null
                  ? currentEmployee.lat.toFixed(6)
                  : null
              }
            />
            <InfoRow
              label={t('employees.form.lng', 'Longitude')}
              value={
                currentEmployee.lng !== null
                  ? currentEmployee.lng.toFixed(6)
                  : null
              }
            />
          </div>
        </Card>
      </div>

      {/* Bottom actions */}
      <div className="flex items-center gap-3">
        <Link to={`/employees/${currentEmployee.id}/edit`}>
          <Button variant="secondary">{t('common.edit', 'Modifier')}</Button>
        </Link>
        <Button variant="danger" onClick={handleDelete}>
          {t('common.delete', 'Supprimer')}
        </Button>
        <Link to="/employees" className="ml-auto">
          <Button variant="ghost">
            {t('employees.back_to_list', 'Retour a la liste')}
          </Button>
        </Link>
      </div>
    </div>
  );
}
