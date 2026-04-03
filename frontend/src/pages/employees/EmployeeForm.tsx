import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { MapPicker } from '@/components/maps/MapPicker';
import { useSiteStore } from '@/stores/siteStore';
import { listPointsArret, type PointArret } from '@/api/vehicles';
import type { EmployeeCreate, OptInChoice } from '@/types/employee';

interface FieldErrors {
  [field: string]: string;
}

interface EmployeeFormProps {
  initialData?: Partial<EmployeeCreate>;
  onSubmit: (data: EmployeeCreate) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
  apiError?: string | null;
  isEditMode?: boolean;
}

const SHIFT_OPTIONS = ['P1', 'P2', 'P3', 'N', 'S'];
const TRANSPORT_MODES = [
  'Voiture',
  'Bus',
  'Tramway',
  'Velo',
  'Marche',
  'Covoiturage',
];
const OPT_IN_OPTIONS: OptInChoice[] = ['Oui', 'Non', 'Sous conditions'];

function SelectField({
  label,
  value,
  onChange,
  options,
  error,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  error?: string;
  placeholder?: string;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={[
          'w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm',
          'outline-none transition-shadow duration-150 appearance-none',
          error
            ? 'ring-2 ring-error/30'
            : 'focus:ring-2 focus:ring-primary/20',
        ].join(' ')}
      >
        {placeholder && (
          <option value="">{placeholder}</option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-sm text-error font-sans" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function ToggleField({
  label,
  checked,
  onChange,
  description,
}: {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  description?: string;
}) {
  return (
    <label className="flex items-start gap-3 cursor-pointer select-none py-2">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="w-4 h-4 rounded accent-primary mt-0.5"
      />
      <div className="flex flex-col gap-0.5">
        <span className="text-sm font-sans text-on-surface">{label}</span>
        {description && (
          <span className="text-xs font-sans text-on-surface-variant">
            {description}
          </span>
        )}
      </div>
    </label>
  );
}

export function EmployeeForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting,
  apiError,
  isEditMode = false,
}: EmployeeFormProps) {
  const { t } = useTranslation();
  const { sites, fetchSites } = useSiteStore();
  const [pointsArret, setPointsArret] = useState<PointArret[]>([]);

  /* Fetch sites and stops for dropdowns */
  useEffect(() => {
    fetchSites({ page: 1, page_size: 100 });
    listPointsArret({ page_size: 500 }).then((r) => setPointsArret(r.items ?? []));
  }, [fetchSites]);

  /* Form state - Identite */
  const [matricule, setMatricule] = useState(initialData?.matricule ?? '');
  const [firstName, setFirstName] = useState(initialData?.first_name ?? '');
  const [lastName, setLastName] = useState(initialData?.last_name ?? '');
  const [phone, setPhone] = useState(initialData?.phone ?? '');
  const [functionRole, setFunctionRole] = useState(
    initialData?.function_role ?? '',
  );
  const [department, setDepartment] = useState(initialData?.department ?? '');

  /* Form state - Affectation */
  const [siteId, setSiteId] = useState(initialData?.site_id ?? '');
  const [shiftTime, setShiftTime] = useState(initialData?.shift_time ?? '');
  const [pointArretId, setPointArretId] = useState(initialData?.point_arret_id ?? '');

  /* Form state - Localisation */
  const [address, setAddress] = useState(initialData?.address ?? '');
  const [quartier, setQuartier] = useState(initialData?.quartier ?? '');
  const [city, setCity] = useState(initialData?.city ?? '');
  const [lat, setLat] = useState(initialData?.lat ?? 33.57);
  const [lng, setLng] = useState(initialData?.lng ?? -7.59);

  /* Form state - Mobilite */
  const [isPmr, setIsPmr] = useState(initialData?.is_pmr ?? false);
  const [transportRequired, setTransportRequired] = useState(
    initialData?.transport_required ?? true,
  );
  const [currentTransportMode, setCurrentTransportMode] = useState(
    initialData?.current_transport_mode ?? '',
  );
  const [optInCompanyTransport, setOptInCompanyTransport] =
    useState<OptInChoice>(initialData?.opt_in_company_transport ?? 'Non');
  const [hasPrivateCar, setHasPrivateCar] = useState(
    initialData?.has_private_car ?? false,
  );
  const [volunteerDriver, setVolunteerDriver] = useState(
    initialData?.volunteer_driver ?? false,
  );
  const [carpoolSeats, setCarpoolSeats] = useState(
    initialData?.carpool_seats ?? 0,
  );

  const [errors, setErrors] = useState<FieldErrors>({});

  const validate = useCallback((): boolean => {
    const newErrors: FieldErrors = {};

    if (!matricule.trim()) {
      newErrors.matricule = t(
        'employees.form.error_required',
        'Ce champ est requis',
      );
    }
    if (!firstName.trim()) {
      newErrors.first_name = t(
        'employees.form.error_required',
        'Ce champ est requis',
      );
    }
    if (!lastName.trim()) {
      newErrors.last_name = t(
        'employees.form.error_required',
        'Ce champ est requis',
      );
    }
    if (!siteId) {
      newErrors.site_id = t(
        'employees.form.error_required',
        'Ce champ est requis',
      );
    }
    if (lat !== null && (lat < -90 || lat > 90)) {
      newErrors.lat = t(
        'employees.form.error_lat',
        'Latitude entre -90 et 90',
      );
    }
    if (lng !== null && (lng < -180 || lng > 180)) {
      newErrors.lng = t(
        'employees.form.error_lng',
        'Longitude entre -180 et 180',
      );
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [matricule, firstName, lastName, siteId, lat, lng, t]);

  const handleSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      if (!validate()) return;

      const data: EmployeeCreate = {
        matricule: matricule.trim(),
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        site_id: siteId,
        shift_time: shiftTime || null,
        point_arret_id: pointArretId || null,
        address: address.trim() || null,
        quartier: quartier.trim() || null,
        city: city.trim() || null,
        lat: lat ?? null,
        lng: lng ?? null,
        is_pmr: isPmr,
        function_role: functionRole.trim() || null,
        phone: phone.trim() || null,
        department: department.trim() || null,
        transport_required: transportRequired,
        current_transport_mode: currentTransportMode || null,
        opt_in_company_transport: optInCompanyTransport,
        has_private_car: hasPrivateCar,
        volunteer_driver: volunteerDriver,
        carpool_seats: volunteerDriver ? carpoolSeats : 0,
      };

      await onSubmit(data);
    },
    [
      validate,
      onSubmit,
      matricule,
      firstName,
      lastName,
      siteId,
      shiftTime,
      address,
      quartier,
      city,
      lat,
      lng,
      isPmr,
      functionRole,
      phone,
      department,
      transportRequired,
      currentTransportMode,
      optInCompanyTransport,
      hasPrivateCar,
      volunteerDriver,
      carpoolSeats,
    ],
  );

  const handleMapChange = useCallback((newLat: number, newLng: number) => {
    setLat(newLat);
    setLng(newLng);
  }, []);

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-8">
      {/* API error banner */}
      {apiError && (
        <div className="bg-error-container rounded-lg p-4">
          <p className="text-error text-sm font-sans">{apiError}</p>
        </div>
      )}

      {/* Section: Identite */}
      <Card title={t('employees.form.section_identity', 'Identite')}>
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label={t('employees.form.matricule', 'Matricule') + ' *'}
              value={matricule}
              onChange={(e) => setMatricule(e.target.value)}
              error={errors.matricule}
              placeholder="EMP-001"
              disabled={isEditMode}
            />
            <Input
              label={t('employees.form.first_name', 'Prenom') + ' *'}
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              error={errors.first_name}
            />
            <Input
              label={t('employees.form.last_name', 'Nom') + ' *'}
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              error={errors.last_name}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label={t('employees.form.phone', 'Telephone')}
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <Input
              label={t('employees.form.function_role', 'Fonction')}
              value={functionRole}
              onChange={(e) => setFunctionRole(e.target.value)}
            />
            <Input
              label={t('employees.form.department', 'Departement')}
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
            />
          </div>
        </div>
      </Card>

      {/* Section: Affectation */}
      <Card title={t('employees.form.section_assignment', 'Affectation')}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SelectField
            label={t('employees.form.site', 'Site') + ' *'}
            value={siteId}
            onChange={setSiteId}
            error={errors.site_id}
            placeholder={t(
              'employees.form.site_placeholder',
              'Selectionner un site...',
            )}
            options={sites.map((s) => ({
              value: s.id,
              label: `${s.code} — ${s.name}`,
            }))}
          />
          <SelectField
            label={t('employees.form.shift_time', 'Horaire')}
            value={shiftTime}
            onChange={setShiftTime}
            placeholder={t(
              'employees.form.shift_placeholder',
              'Selectionner un horaire...',
            )}
            options={SHIFT_OPTIONS.map((s) => ({
              value: s,
              label: s,
            }))}
          />
          <SelectField
            label={t('employees.form.point_arret', "Point d'arrêt")}
            value={pointArretId}
            onChange={setPointArretId}
            placeholder={t(
              'employees.form.point_arret_placeholder',
              "Selectionner un arrêt...",
            )}
            options={pointsArret.map((p) => ({
              value: p.id,
              label: `${p.code} — ${p.nom}${p.ville ? ` (${p.ville})` : ''}`,
            }))}
          />
        </div>
      </Card>

      {/* Section: Localisation */}
      <Card title={t('employees.form.section_location', 'Localisation')}>
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label={t('employees.form.address', 'Adresse')}
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
            <Input
              label={t('employees.form.quartier', 'Quartier')}
              value={quartier}
              onChange={(e) => setQuartier(e.target.value)}
            />
            <Input
              label={t('employees.form.city', 'Ville')}
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label={t('employees.form.lat', 'Latitude')}
              type="number"
              value={String(lat)}
              onChange={(e) => setLat(parseFloat(e.target.value) || 0)}
              error={errors.lat}
              step="0.000001"
              min="-90"
              max="90"
            />
            <Input
              label={t('employees.form.lng', 'Longitude')}
              type="number"
              value={String(lng)}
              onChange={(e) => setLng(parseFloat(e.target.value) || 0)}
              error={errors.lng}
              step="0.000001"
              min="-180"
              max="180"
            />
          </div>
          <MapPicker lat={lat} lng={lng} onChange={handleMapChange} height="300px" />
        </div>
      </Card>

      {/* Section: Mobilite */}
      <Card title={t('employees.form.section_mobility', 'Mobilite')}>
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ToggleField
              label={t('employees.form.is_pmr', 'Personne a mobilite reduite (PMR)')}
              checked={isPmr}
              onChange={setIsPmr}
            />
            <ToggleField
              label={t(
                'employees.form.transport_required',
                'Transport requis',
              )}
              checked={transportRequired}
              onChange={setTransportRequired}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SelectField
              label={t(
                'employees.form.current_transport_mode',
                'Mode de transport actuel',
              )}
              value={currentTransportMode}
              onChange={setCurrentTransportMode}
              placeholder={t(
                'employees.form.transport_mode_placeholder',
                'Selectionner un mode...',
              )}
              options={TRANSPORT_MODES.map((m) => ({
                value: m,
                label: m,
              }))}
            />
            <SelectField
              label={t(
                'employees.form.opt_in_company_transport',
                'Opt-in transport entreprise',
              )}
              value={optInCompanyTransport}
              onChange={(v) => setOptInCompanyTransport(v as OptInChoice)}
              options={OPT_IN_OPTIONS.map((o) => ({
                value: o,
                label: o,
              }))}
            />
          </div>

          <div className="bg-surface-container-low/50 rounded-xl p-5">
            <div className="flex flex-col gap-3">
              <ToggleField
                label={t(
                  'employees.form.has_private_car',
                  'Possede un vehicule personnel',
                )}
                checked={hasPrivateCar}
                onChange={setHasPrivateCar}
              />
              <ToggleField
                label={t(
                  'employees.form.volunteer_driver',
                  'Conducteur volontaire (covoiturage)',
                )}
                checked={volunteerDriver}
                onChange={setVolunteerDriver}
              />
              {volunteerDriver && (
                <div className="max-w-xs">
                  <Input
                    label={t(
                      'employees.form.carpool_seats',
                      'Places de covoiturage disponibles',
                    )}
                    type="number"
                    value={String(carpoolSeats)}
                    onChange={(e) =>
                      setCarpoolSeats(parseInt(e.target.value, 10) || 0)
                    }
                    min="1"
                    max="8"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex items-center gap-4 justify-end">
        <Button variant="ghost" type="button" onClick={onCancel}>
          {t('common.cancel')}
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          {t('common.save')}
        </Button>
      </div>
    </form>
  );
}
