import { useCallback, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { MapPicker } from '@/components/maps/MapPicker';
import type { SiteCreate, SecurityProfile } from '@/types/site';

interface FieldErrors {
  [field: string]: string;
}

interface SiteFormProps {
  initialData?: Partial<SiteCreate>;
  onSubmit: (data: SiteCreate) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
  apiError?: string | null;
}

const SECURITY_OPTIONS: SecurityProfile[] = ['normal', 'elevated', 'critical'];
const SHIFT_OPTIONS = [1, 2, 3];
const DEFAULT_WORKING_DAYS = 'Lun-Ven';

function TextArea({
  label,
  value,
  onChange,
  error,
  rows = 3,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  rows?: number;
}) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
        {label}
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={rows}
        className={[
          'w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm',
          'placeholder:text-on-surface-variant/50',
          'outline-none transition-all duration-150 resize-y',
          error
            ? 'ring-1 ring-error/40'
            : 'focus:ring-1 focus:ring-primary/20 focus:bg-surface-container-lowest',
        ].join(' ')}
      />
      {error && (
        <p className="text-xs text-error font-sans" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
  error,
}: {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  options: { value: string | number; label: string }[];
  error?: string;
}) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={[
          'w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm',
          'outline-none transition-all duration-150 appearance-none',
          error
            ? 'ring-1 ring-error/40'
            : 'focus:ring-1 focus:ring-primary/20 focus:bg-surface-container-lowest',
        ].join(' ')}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-xs text-error font-sans" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

export function SiteForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting,
  apiError,
}: SiteFormProps) {
  const { t } = useTranslation();

  /* Form state */
  const [code, setCode] = useState(initialData?.code ?? '');
  const [name, setName] = useState(initialData?.name ?? '');
  const [address, setAddress] = useState(initialData?.address ?? '');
  const [city, setCity] = useState(initialData?.city ?? '');
  const [lat, setLat] = useState(initialData?.lat ?? 33.57);
  const [lng, setLng] = useState(initialData?.lng ?? -7.59);
  const [numShifts, setNumShifts] = useState(initialData?.num_shifts ?? 1);

  const [shift1Entry, setShift1Entry] = useState(initialData?.shift_1_entry ?? '');
  const [shift1Exit, setShift1Exit] = useState(initialData?.shift_1_exit ?? '');
  const [shift2Entry, setShift2Entry] = useState(initialData?.shift_2_entry ?? '');
  const [shift2Exit, setShift2Exit] = useState(initialData?.shift_2_exit ?? '');
  const [shift3Entry, setShift3Entry] = useState(initialData?.shift_3_entry ?? '');
  const [shift3Exit, setShift3Exit] = useState(initialData?.shift_3_exit ?? '');

  const [workingDays, setWorkingDays] = useState(
    initialData?.working_days ?? DEFAULT_WORKING_DAYS,
  );
  const [daysPerWeek, setDaysPerWeek] = useState(initialData?.days_per_week ?? 5);
  const [zfeZone, setZfeZone] = useState(initialData?.zfe_zone ?? false);
  const [securityProfile, setSecurityProfile] = useState<SecurityProfile>(
    initialData?.security_profile ?? 'normal',
  );

  const [contactName, setContactName] = useState(initialData?.contact_name ?? '');
  const [contactPhone, setContactPhone] = useState(initialData?.contact_phone ?? '');

  const [accessNotes, setAccessNotes] = useState(initialData?.access_notes ?? '');
  const [parkingNotes, setParkingNotes] = useState(initialData?.parking_notes ?? '');
  const [observations, setObservations] = useState(initialData?.observations ?? '');

  const [errors, setErrors] = useState<FieldErrors>({});

  const validate = useCallback((): boolean => {
    const newErrors: FieldErrors = {};

    if (!code.trim()) {
      newErrors.code = t('sites.form.error_required', 'Ce champ est requis');
    }
    if (!name.trim()) {
      newErrors.name = t('sites.form.error_required', 'Ce champ est requis');
    }
    if (!address.trim()) {
      newErrors.address = t('sites.form.error_required', 'Ce champ est requis');
    }
    if (!city.trim()) {
      newErrors.city = t('sites.form.error_required', 'Ce champ est requis');
    }
    if (lat < -90 || lat > 90) {
      newErrors.lat = t('sites.form.error_lat', 'Latitude entre -90 et 90');
    }
    if (lng < -180 || lng > 180) {
      newErrors.lng = t('sites.form.error_lng', 'Longitude entre -180 et 180');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [code, name, address, city, lat, lng, t]);

  const handleSubmit = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      if (!validate()) return;

      const data: SiteCreate = {
        code: code.trim(),
        name: name.trim(),
        address: address.trim(),
        city: city.trim(),
        lat,
        lng,
        num_shifts: numShifts,
        shift_1_entry: shift1Entry || null,
        shift_1_exit: shift1Exit || null,
        shift_2_entry: numShifts >= 2 ? shift2Entry || null : null,
        shift_2_exit: numShifts >= 2 ? shift2Exit || null : null,
        shift_3_entry: numShifts >= 3 ? shift3Entry || null : null,
        shift_3_exit: numShifts >= 3 ? shift3Exit || null : null,
        working_days: workingDays.trim(),
        days_per_week: daysPerWeek,
        zfe_zone: zfeZone,
        security_profile: securityProfile,
        contact_name: contactName || null,
        contact_phone: contactPhone || null,
        access_notes: accessNotes || null,
        parking_notes: parkingNotes || null,
        observations: observations || null,
      };

      await onSubmit(data);
    },
    [
      validate,
      onSubmit,
      code, name, address, city, lat, lng, numShifts,
      shift1Entry, shift1Exit, shift2Entry, shift2Exit, shift3Entry, shift3Exit,
      workingDays, daysPerWeek, zfeZone, securityProfile,
      contactName, contactPhone, accessNotes, parkingNotes, observations,
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
        <div className="bg-error-container rounded-xl p-4 flex items-center gap-3">
          <span className="material-symbols-outlined text-error text-lg">error</span>
          <p className="text-error text-sm font-sans">{apiError}</p>
        </div>
      )}

      {/* Section: Identification */}
      <Card title={t('sites.form.section_id', 'Identification')}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <Input
            label={t('sites.form.code', 'Code') + ' *'}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            error={errors.code}
            placeholder="SITE-001"
          />
          <Input
            label={t('sites.form.name', 'Nom') + ' *'}
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={errors.name}
            placeholder={t('sites.form.name_placeholder', 'Nom du site')}
          />
        </div>
      </Card>

      {/* Section: Localisation */}
      <Card title={t('sites.form.section_location', 'Localisation')}>
        <div className="flex flex-col gap-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Input
              label={t('sites.form.address', 'Adresse') + ' *'}
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              error={errors.address}
            />
            <Input
              label={t('sites.form.city', 'Ville') + ' *'}
              value={city}
              onChange={(e) => setCity(e.target.value)}
              error={errors.city}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Input
              label={t('sites.form.lat', 'Latitude') + ' *'}
              type="number"
              value={String(lat)}
              onChange={(e) => setLat(parseFloat(e.target.value) || 0)}
              error={errors.lat}
              step="0.000001"
              min="-90"
              max="90"
            />
            <Input
              label={t('sites.form.lng', 'Longitude') + ' *'}
              type="number"
              value={String(lng)}
              onChange={(e) => setLng(parseFloat(e.target.value) || 0)}
              error={errors.lng}
              step="0.000001"
              min="-180"
              max="180"
            />
          </div>
          <div className="rounded-xl overflow-hidden">
            <MapPicker lat={lat} lng={lng} onChange={handleMapChange} height="350px" />
          </div>
        </div>
      </Card>

      {/* Section: Horaires */}
      <Card title={t('sites.form.section_shifts', 'Horaires')}>
        <div className="flex flex-col gap-5">
          <SelectField
            label={t('sites.form.num_shifts', "Nombre d'equipes")}
            value={numShifts}
            onChange={(v) => setNumShifts(parseInt(v, 10))}
            options={SHIFT_OPTIONS.map((n) => ({
              value: n,
              label: `${n} ${t('sites.form.shift_label', 'equipe(s)')}`,
            }))}
          />

          {/* Shift 1 */}
          <div className="bg-blue-50/50 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px] font-black">M</span>
              <p className="text-sm font-bold text-on-surface font-sans">
                {t('sites.form.shift_n', 'Equipe {{n}}', { n: 1 })}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-5">
              <Input
                label={t('sites.form.entry_time', 'Heure entree')}
                type="time"
                value={shift1Entry}
                onChange={(e) => setShift1Entry(e.target.value)}
              />
              <Input
                label={t('sites.form.exit_time', 'Heure sortie')}
                type="time"
                value={shift1Exit}
                onChange={(e) => setShift1Exit(e.target.value)}
              />
            </div>
          </div>

          {/* Shift 2 */}
          {numShifts >= 2 && (
            <div className="bg-amber-50/50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <span className="w-6 h-6 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center text-[10px] font-black">A</span>
                <p className="text-sm font-bold text-on-surface font-sans">
                  {t('sites.form.shift_n', 'Equipe {{n}}', { n: 2 })}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-5">
                <Input
                  label={t('sites.form.entry_time', 'Heure entree')}
                  type="time"
                  value={shift2Entry}
                  onChange={(e) => setShift2Entry(e.target.value)}
                />
                <Input
                  label={t('sites.form.exit_time', 'Heure sortie')}
                  type="time"
                  value={shift2Exit}
                  onChange={(e) => setShift2Exit(e.target.value)}
                />
              </div>
            </div>
          )}

          {/* Shift 3 */}
          {numShifts >= 3 && (
            <div className="bg-indigo-50/50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-[10px] font-black">N</span>
                <p className="text-sm font-bold text-on-surface font-sans">
                  {t('sites.form.shift_n', 'Equipe {{n}}', { n: 3 })}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-5">
                <Input
                  label={t('sites.form.entry_time', 'Heure entree')}
                  type="time"
                  value={shift3Entry}
                  onChange={(e) => setShift3Entry(e.target.value)}
                />
                <Input
                  label={t('sites.form.exit_time', 'Heure sortie')}
                  type="time"
                  value={shift3Exit}
                  onChange={(e) => setShift3Exit(e.target.value)}
                />
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Section: Configuration */}
      <Card title={t('sites.form.section_config', 'Configuration')}>
        <div className="flex flex-col gap-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Input
              label={t('sites.form.working_days', 'Jours travailles')}
              value={workingDays}
              onChange={(e) => setWorkingDays(e.target.value)}
              placeholder="Lun-Ven"
            />
            <Input
              label={t('sites.form.days_per_week', 'Jours par semaine')}
              type="number"
              value={String(daysPerWeek)}
              onChange={(e) => setDaysPerWeek(parseInt(e.target.value, 10) || 5)}
              min="1"
              max="7"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 items-end">
            <label className="flex items-center gap-3 cursor-pointer select-none py-2.5 px-4 rounded-xl bg-surface-container-low hover:bg-surface-container transition-colors">
              <input
                type="checkbox"
                checked={zfeZone}
                onChange={(e) => setZfeZone(e.target.checked)}
                className="w-4 h-4 rounded accent-primary"
              />
              <div className="flex flex-col">
                <span className="text-sm font-sans font-medium text-on-surface">
                  {t('sites.form.zfe_zone', 'Zone a Faibles Emissions (ZFE)')}
                </span>
                <span className="text-[10px] text-on-surface-variant font-sans">
                  {t('sites.form.zfe_hint', 'Contraintes vehicules electriques/hybrides')}
                </span>
              </div>
            </label>

            <SelectField
              label={t('sites.form.security_profile', 'Profil de securite')}
              value={securityProfile}
              onChange={(v) => setSecurityProfile(v as SecurityProfile)}
              options={SECURITY_OPTIONS.map((p) => ({
                value: p,
                label:
                  p === 'normal'
                    ? t('sites.security.normal', 'Normal')
                    : p === 'elevated'
                      ? t('sites.security.elevated', 'Eleve')
                      : t('sites.security.critical', 'Critique'),
              }))}
            />
          </div>
        </div>
      </Card>

      {/* Section: Contact */}
      <Card title={t('sites.form.section_contact', 'Contact')}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <Input
            label={t('sites.form.contact_name', 'Nom du contact')}
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
          />
          <Input
            label={t('sites.form.contact_phone', 'Telephone')}
            type="tel"
            value={contactPhone}
            onChange={(e) => setContactPhone(e.target.value)}
          />
        </div>
      </Card>

      {/* Section: Notes */}
      <Card title={t('sites.form.section_notes', 'Notes')}>
        <div className="flex flex-col gap-5">
          <TextArea
            label={t('sites.form.access_notes', "Notes d'acces")}
            value={accessNotes}
            onChange={setAccessNotes}
          />
          <TextArea
            label={t('sites.form.parking_notes', 'Notes de parking')}
            value={parkingNotes}
            onChange={setParkingNotes}
          />
          <TextArea
            label={t('sites.form.observations', 'Observations')}
            value={observations}
            onChange={setObservations}
          />
        </div>
      </Card>

      {/* Actions */}
      <div className="flex items-center gap-4 justify-end">
        <Button variant="ghost" type="button" onClick={onCancel}>
          {t('common.cancel')}
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          <span className="material-symbols-outlined text-base mr-1.5">save</span>
          {t('common.save')}
        </Button>
      </div>
    </form>
  );
}
