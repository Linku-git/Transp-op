import { useCallback, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { MapPicker } from '@/components/maps/MapPicker';
import { ShiftsEditorTable } from '@/components/shifts/ShiftsEditorTable';
import {
  WorkingDayRangePicker,
  workingDaysToRange,
  rangeToWorkingDays,
  rangeToDaysPerWeek,
} from '@/components/ui/WorkingDayRangePicker';
import type { SiteCreate, SecurityProfile } from '@/types/site';

interface FieldErrors { [field: string]: string; }

interface SiteFormProps {
  initialData?: Partial<SiteCreate>;
  onSubmit: (data: SiteCreate) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
  apiError?: string | null;
}

const SECURITY_OPTIONS: SecurityProfile[] = ['normal', 'elevated', 'critical'];

function TextArea({ label, value, onChange, rows = 3 }: {
  label: string; value: string; onChange: (v: string) => void; rows?: number;
}) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={rows}
        className="w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm placeholder:text-on-surface-variant/50 outline-none transition-all duration-150 resize-y focus:ring-1 focus:ring-primary/20 focus:bg-surface-container-lowest"
      />
    </div>
  );
}

function SelectField({ label, value, onChange, options, error }: {
  label: string; value: string | number; onChange: (v: string) => void;
  options: { value: string | number; label: string }[]; error?: string;
}) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={[
          'w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none transition-all duration-150 appearance-none',
          error ? 'ring-1 ring-error/40' : 'focus:ring-1 focus:ring-primary/20 focus:bg-surface-container-lowest',
        ].join(' ')}
      >
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
      {error && <p className="text-xs text-error font-sans">{error}</p>}
    </div>
  );
}

function parseInitialRange(wd: string | null | undefined): { startIdx: number; endIdx: number } {
  if (!wd) return { startIdx: 0, endIdx: 4 };
  return workingDaysToRange(wd);
}

export function SiteForm({ initialData, onSubmit, onCancel, isSubmitting, apiError }: SiteFormProps) {
  const { t } = useTranslation();

  const [code, setCode] = useState(initialData?.code ?? '');
  const [name, setName] = useState(initialData?.name ?? '');
  const [address, setAddress] = useState(initialData?.address ?? '');
  const [city, setCity] = useState(initialData?.city ?? '');
  const [lat, setLat] = useState(initialData?.lat ?? 33.57);
  const [lng, setLng] = useState(initialData?.lng ?? -7.59);

  const initRange = parseInitialRange(initialData?.working_days);
  const [startIdx, setStartIdx] = useState(initRange.startIdx);
  const [endIdx, setEndIdx] = useState(initRange.endIdx);

  const [zfeZone, setZfeZone] = useState(initialData?.zfe_zone ?? false);
  const [securityProfile, setSecurityProfile] = useState<SecurityProfile>(initialData?.security_profile ?? 'normal');
  const [contactName, setContactName] = useState(initialData?.contact_name ?? '');
  const [contactPhone, setContactPhone] = useState(initialData?.contact_phone ?? '');
  const [accessNotes, setAccessNotes] = useState(initialData?.access_notes ?? '');
  const [parkingNotes, setParkingNotes] = useState(initialData?.parking_notes ?? '');
  const [observations, setObservations] = useState(initialData?.observations ?? '');

  const [errors, setErrors] = useState<FieldErrors>({});

  const validate = useCallback((): boolean => {
    const e: FieldErrors = {};
    if (!code.trim()) e.code = t('sites.form.error_required', 'Ce champ est requis');
    if (!name.trim()) e.name = t('sites.form.error_required', 'Ce champ est requis');
    if (!address.trim()) e.address = t('sites.form.error_required', 'Ce champ est requis');
    if (!city.trim()) e.city = t('sites.form.error_required', 'Ce champ est requis');
    if (lat < -90 || lat > 90) e.lat = t('sites.form.error_lat', 'Latitude entre -90 et 90');
    if (lng < -180 || lng > 180) e.lng = t('sites.form.error_lng', 'Longitude entre -180 et 180');
    setErrors(e);
    return Object.keys(e).length === 0;
  }, [code, name, address, city, lat, lng, t]);

  const handleSubmit = useCallback(async (ev: FormEvent) => {
    ev.preventDefault();
    if (!validate()) return;

    const data: SiteCreate = {
      code: code.trim(), name: name.trim(), address: address.trim(), city: city.trim(),
      lat, lng,
      num_shifts: 1,
      working_days: rangeToWorkingDays(startIdx, endIdx),
      days_per_week: rangeToDaysPerWeek(startIdx, endIdx),
      zfe_zone: zfeZone,
      security_profile: securityProfile,
      contact_name: contactName || null,
      contact_phone: contactPhone || null,
      access_notes: accessNotes || null,
      parking_notes: parkingNotes || null,
      observations: observations || null,
    };
    await onSubmit(data);
  }, [
    validate, onSubmit, code, name, address, city, lat, lng,
    startIdx, endIdx, zfeZone, securityProfile,
    contactName, contactPhone, accessNotes, parkingNotes, observations,
  ]);

  const handleMapChange = useCallback((newLat: number, newLng: number) => {
    setLat(newLat); setLng(newLng);
  }, []);

  const handleRangeChange = useCallback((s: number, e: number) => {
    setStartIdx(s);
    setEndIdx(e);
  }, []);

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-8">
      {apiError && (
        <div className="bg-error-container rounded-xl p-4 flex items-center gap-3">
          <span className="material-symbols-outlined text-error text-lg">error</span>
          <p className="text-error text-sm font-sans">{apiError}</p>
        </div>
      )}

      {/* Identification */}
      <Card title={t('sites.form.section_id', 'Identification')}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <Input label={t('sites.form.code', 'Code') + ' *'} value={code} onChange={(e) => setCode(e.target.value)} error={errors.code} placeholder="SITE-001" />
          <Input label={t('sites.form.name', 'Nom') + ' *'} value={name} onChange={(e) => setName(e.target.value)} error={errors.name} placeholder={t('sites.form.name_placeholder', 'Nom du site')} />
        </div>
      </Card>

      {/* Localisation */}
      <Card title={t('sites.form.section_location', 'Localisation')}>
        <div className="flex flex-col gap-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Input label={t('sites.form.address', 'Adresse') + ' *'} value={address} onChange={(e) => setAddress(e.target.value)} error={errors.address} />
            <Input label={t('sites.form.city', 'Ville') + ' *'} value={city} onChange={(e) => setCity(e.target.value)} error={errors.city} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Input label={t('sites.form.lat', 'Latitude') + ' *'} type="number" value={String(lat)} onChange={(e) => setLat(parseFloat(e.target.value) || 0)} error={errors.lat} step="0.000001" min="-90" max="90" />
            <Input label={t('sites.form.lng', 'Longitude') + ' *'} type="number" value={String(lng)} onChange={(e) => setLng(parseFloat(e.target.value) || 0)} error={errors.lng} step="0.000001" min="-180" max="180" />
          </div>
          <div className="rounded-xl overflow-hidden">
            <MapPicker lat={lat} lng={lng} onChange={handleMapChange} height="350px" />
          </div>
        </div>
      </Card>

      {/* Horaires — company-wide, managed via HoraireTravail API */}
      <Card title={t('sites.form.section_shifts', 'Horaires')}>
        <ShiftsEditorTable siteId={null} />
      </Card>

      {/* Configuration */}
      <Card title={t('sites.form.section_config', 'Configuration')}>
        <div className="flex flex-col gap-6">

          {/* Day range picker */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between mb-1">
              <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
                {t('sites.form.working_days', 'Jours Travaillés')}
              </label>
              <span className="text-xs font-bold text-on-surface bg-surface-container px-2.5 py-1 rounded-full">
                {rangeToDaysPerWeek(startIdx, endIdx)} jour{rangeToDaysPerWeek(startIdx, endIdx) > 1 ? 's' : ''} / semaine
              </span>
            </div>
            <div className="bg-surface-container-low/40 rounded-2xl p-4">
              <WorkingDayRangePicker
                startIdx={startIdx}
                endIdx={endIdx}
                onChange={handleRangeChange}
              />
            </div>
          </div>

          {/* ZFE + Security */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 items-end">
            <label className="flex items-center gap-3 cursor-pointer select-none py-2.5 px-4 rounded-xl bg-surface-container-low hover:bg-surface-container transition-colors">
              <input type="checkbox" checked={zfeZone} onChange={(e) => setZfeZone(e.target.checked)} className="w-4 h-4 rounded accent-primary" />
              <div className="flex flex-col">
                <span className="text-sm font-sans font-medium text-on-surface">{t('sites.form.zfe_zone', 'Zone a Faibles Emissions (ZFE)')}</span>
                <span className="text-[10px] text-on-surface-variant font-sans">{t('sites.form.zfe_hint', 'Contraintes vehicules electriques/hybrides')}</span>
              </div>
            </label>
            <SelectField
              label={t('sites.form.security_profile', 'Profil de securite')}
              value={securityProfile}
              onChange={(v) => setSecurityProfile(v as SecurityProfile)}
              options={SECURITY_OPTIONS.map((p) => ({
                value: p,
                label: p === 'normal' ? t('sites.security.normal', 'Normal') : p === 'elevated' ? t('sites.security.elevated', 'Eleve') : t('sites.security.critical', 'Critique'),
              }))}
            />
          </div>
        </div>
      </Card>

      {/* Contact */}
      <Card title={t('sites.form.section_contact', 'Contact')}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <Input label={t('sites.form.contact_name', 'Nom du contact')} value={contactName} onChange={(e) => setContactName(e.target.value)} />
          <Input label={t('sites.form.contact_phone', 'Telephone')} type="tel" value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} />
        </div>
      </Card>

      {/* Notes */}
      <Card title={t('sites.form.section_notes', 'Notes')}>
        <div className="flex flex-col gap-5">
          <TextArea label={t('sites.form.access_notes', "Notes d'acces")} value={accessNotes} onChange={setAccessNotes} />
          <TextArea label={t('sites.form.parking_notes', 'Notes de parking')} value={parkingNotes} onChange={setParkingNotes} />
          <TextArea label={t('sites.form.observations', 'Observations')} value={observations} onChange={setObservations} />
        </div>
      </Card>

      <div className="flex items-center gap-4 justify-end">
        <Button variant="ghost" type="button" onClick={onCancel}>{t('common.cancel')}</Button>
        <Button type="submit" isLoading={isSubmitting}>
          <span className="material-symbols-outlined text-base mr-1.5">save</span>
          {t('common.save')}
        </Button>
      </div>
    </form>
  );
}
