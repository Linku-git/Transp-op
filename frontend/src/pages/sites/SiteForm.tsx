import { useCallback, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { MapPicker } from '@/components/maps/MapPicker';
import type { SiteCreate, SecurityProfile, ShiftType } from '@/types/site';
import { SHIFT_PRESETS, ALL_SHIFT_TYPES } from '@/types/site';

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

interface ShiftState {
  type: string;
  depart_h1: string;
  retour_h1: string;
  depart_h2: string;
  retour_h2: string;
}

const EMPTY_SHIFT: ShiftState = { type: '', depart_h1: '', retour_h1: '', depart_h2: '', retour_h2: '' };

const SECURITY_OPTIONS: SecurityProfile[] = ['normal', 'elevated', 'critical'];
const SHIFT_OPTIONS = [1, 2, 3];
const DEFAULT_WORKING_DAYS = 'Lun-Ven';

const SHIFT_COLORS = [
  { bg: 'bg-blue-50/60', badge: 'bg-blue-100 text-blue-700', label: 'M' },
  { bg: 'bg-amber-50/60', badge: 'bg-amber-100 text-amber-700', label: 'A' },
  { bg: 'bg-indigo-50/60', badge: 'bg-indigo-100 text-indigo-700', label: 'N' },
];

function TextArea({
  label, value, onChange, rows = 3,
}: {
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

function SelectField({
  label, value, onChange, options, error,
}: {
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

function TimeInput({
  label, value, onChange, hint,
}: {
  label: string; value: string; onChange: (v: string) => void; hint?: string;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">{label}</label>
      {hint && <span className="text-[9px] text-on-surface-variant font-sans uppercase tracking-wider">{hint}</span>}
      <input
        type="time"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none transition-all duration-150 focus:ring-1 focus:ring-primary/20 focus:bg-surface-container-lowest"
      />
    </div>
  );
}

function ShiftCard({
  index, shift, onChange,
}: {
  index: number; shift: ShiftState; onChange: (s: ShiftState) => void;
}) {
  const { t } = useTranslation();
  const colors = SHIFT_COLORS[index];

  const handleTypeChange = (type: string) => {
    if (type && type !== 'Personnalisé' && type in SHIFT_PRESETS) {
      const preset = SHIFT_PRESETS[type as ShiftType];
      onChange({
        type,
        depart_h1: preset.depart_h1,
        retour_h1: preset.retour_h1,
        depart_h2: preset.depart_h2 ?? '',
        retour_h2: preset.retour_h2 ?? '',
      });
    } else {
      onChange({ ...shift, type });
    }
  };

  const showDepartH2 = shift.type === 'Sirène' || shift.type === 'Personnalisé' || shift.depart_h2 !== '';
  const showRetourH2 = shift.type === 'Poste 1' || shift.type === 'Poste 2' || shift.type === 'Poste 3' ||
    shift.type === 'Sirène' || shift.type === 'Personnalisé' || shift.retour_h2 !== '';

  return (
    <div className={`${colors.bg} rounded-xl p-5`}>
      <div className="flex items-center gap-2 mb-4">
        <span className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black ${colors.badge}`}>
          {colors.label}
        </span>
        <p className="text-sm font-bold text-on-surface font-sans">
          {t('sites.form.shift_n', 'Equipe {{n}}', { n: index + 1 })}
        </p>
      </div>

      <div className="flex flex-col gap-4">
        <SelectField
          label={t('sites.form.shift_type', 'Type horaire')}
          value={shift.type}
          onChange={handleTypeChange}
          options={[
            { value: '', label: t('sites.form.shift_type_select', '— Sélectionner un type —') },
            ...ALL_SHIFT_TYPES.map((st) => ({ value: st, label: st })),
          ]}
        />

        {shift.type && (
          <>
            <div className="border-t border-outline-variant/20 pt-3">
              <p className="text-[9px] font-bold uppercase tracking-widest text-on-surface-variant font-sans mb-3">
                {t('sites.form.premier_horaire', 'Premier Horaire')}
              </p>
              <div className="grid grid-cols-2 gap-4">
                <TimeInput
                  label={t('sites.form.horaire_depart', 'Horaire départ')}
                  value={shift.depart_h1}
                  onChange={(v) => onChange({ ...shift, depart_h1: v })}
                />
                <TimeInput
                  label={t('sites.form.horaire_retour', 'Horaire retour')}
                  value={shift.retour_h1}
                  onChange={(v) => onChange({ ...shift, retour_h1: v })}
                />
              </div>
            </div>

            {(showDepartH2 || showRetourH2) && (
              <div className="border-t border-outline-variant/20 pt-3">
                <p className="text-[9px] font-bold uppercase tracking-widest text-on-surface-variant font-sans mb-3">
                  {t('sites.form.deuxieme_horaire', 'Deuxième Horaire')}
                </p>
                <div className="grid grid-cols-2 gap-4">
                  <TimeInput
                    label={t('sites.form.horaire_depart', 'Horaire départ')}
                    value={shift.depart_h2}
                    onChange={(v) => onChange({ ...shift, depart_h2: v })}
                    hint={!showDepartH2 ? t('sites.form.na', 'N/A') : undefined}
                  />
                  <TimeInput
                    label={t('sites.form.horaire_retour', 'Horaire retour')}
                    value={shift.retour_h2}
                    onChange={(v) => onChange({ ...shift, retour_h2: v })}
                  />
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function initShift(
  type: string | null | undefined,
  entry: string | null | undefined,
  exit_: string | null | undefined,
  dh2: string | null | undefined,
  rh2: string | null | undefined,
): ShiftState {
  return {
    type: type ?? '',
    depart_h1: entry ?? '',
    retour_h1: exit_ ?? '',
    depart_h2: dh2 ?? '',
    retour_h2: rh2 ?? '',
  };
}

export function SiteForm({
  initialData, onSubmit, onCancel, isSubmitting, apiError,
}: SiteFormProps) {
  const { t } = useTranslation();

  const [code, setCode] = useState(initialData?.code ?? '');
  const [name, setName] = useState(initialData?.name ?? '');
  const [address, setAddress] = useState(initialData?.address ?? '');
  const [city, setCity] = useState(initialData?.city ?? '');
  const [lat, setLat] = useState(initialData?.lat ?? 33.57);
  const [lng, setLng] = useState(initialData?.lng ?? -7.59);
  const [numShifts, setNumShifts] = useState(initialData?.num_shifts ?? 1);

  const [shifts, setShifts] = useState<[ShiftState, ShiftState, ShiftState]>([
    initShift(initialData?.shift_1_type, initialData?.shift_1_entry, initialData?.shift_1_exit, initialData?.shift_1_depart_h2, initialData?.shift_1_retour_h2),
    initShift(initialData?.shift_2_type, initialData?.shift_2_entry, initialData?.shift_2_exit, initialData?.shift_2_depart_h2, initialData?.shift_2_retour_h2),
    initShift(initialData?.shift_3_type, initialData?.shift_3_entry, initialData?.shift_3_exit, initialData?.shift_3_depart_h2, initialData?.shift_3_retour_h2),
  ]);

  const updateShift = (idx: number, s: ShiftState) => {
    setShifts((prev) => {
      const next: [ShiftState, ShiftState, ShiftState] = [...prev] as [ShiftState, ShiftState, ShiftState];
      next[idx] = s;
      return next;
    });
  };

  const [workingDays, setWorkingDays] = useState(initialData?.working_days ?? DEFAULT_WORKING_DAYS);
  const [daysPerWeek, setDaysPerWeek] = useState(initialData?.days_per_week ?? 5);
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

    const s1 = shifts[0];
    const s2 = shifts[1];
    const s3 = shifts[2];

    const data: SiteCreate = {
      code: code.trim(), name: name.trim(), address: address.trim(), city: city.trim(),
      lat, lng, num_shifts: numShifts,
      shift_1_type: s1.type || null,
      shift_1_entry: s1.depart_h1 || null,
      shift_1_exit: s1.retour_h1 || null,
      shift_1_depart_h2: s1.depart_h2 || null,
      shift_1_retour_h2: s1.retour_h2 || null,
      shift_2_type: numShifts >= 2 ? s2.type || null : null,
      shift_2_entry: numShifts >= 2 ? s2.depart_h1 || null : null,
      shift_2_exit: numShifts >= 2 ? s2.retour_h1 || null : null,
      shift_2_depart_h2: numShifts >= 2 ? s2.depart_h2 || null : null,
      shift_2_retour_h2: numShifts >= 2 ? s2.retour_h2 || null : null,
      shift_3_type: numShifts >= 3 ? s3.type || null : null,
      shift_3_entry: numShifts >= 3 ? s3.depart_h1 || null : null,
      shift_3_exit: numShifts >= 3 ? s3.retour_h1 || null : null,
      shift_3_depart_h2: numShifts >= 3 ? s3.depart_h2 || null : null,
      shift_3_retour_h2: numShifts >= 3 ? s3.retour_h2 || null : null,
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
  }, [
    validate, onSubmit, code, name, address, city, lat, lng, numShifts, shifts,
    workingDays, daysPerWeek, zfeZone, securityProfile,
    contactName, contactPhone, accessNotes, parkingNotes, observations,
  ]);

  const handleMapChange = useCallback((newLat: number, newLng: number) => {
    setLat(newLat); setLng(newLng);
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

      {/* Horaires */}
      <Card title={t('sites.form.section_shifts', 'Horaires')}>
        <div className="flex flex-col gap-5">
          <SelectField
            label={t('sites.form.num_shifts', "Nombre d'equipes")}
            value={numShifts}
            onChange={(v) => setNumShifts(parseInt(v, 10))}
            options={SHIFT_OPTIONS.map((n) => ({ value: n, label: `${n} ${t('sites.form.shift_label', 'equipe(s)')}` }))}
          />

          {/* Reference table */}
          <div className="rounded-xl overflow-hidden border border-outline-variant/20">
            <table className="w-full text-xs font-sans">
              <thead>
                <tr className="bg-surface-container-low">
                  <th className="text-left p-2.5 font-bold text-on-surface-variant uppercase tracking-wider text-[10px]">Type Horaire</th>
                  <th className="text-center p-2.5 font-bold text-on-surface-variant uppercase tracking-wider text-[10px]">Départ H1</th>
                  <th className="text-center p-2.5 font-bold text-on-surface-variant uppercase tracking-wider text-[10px]">Retour H1</th>
                  <th className="text-center p-2.5 font-bold text-on-surface-variant uppercase tracking-wider text-[10px]">Départ H2</th>
                  <th className="text-center p-2.5 font-bold text-on-surface-variant uppercase tracking-wider text-[10px]">Retour H2</th>
                </tr>
              </thead>
              <tbody>
                {(Object.entries(SHIFT_PRESETS) as [ShiftType, typeof SHIFT_PRESETS[ShiftType]][])
                  .filter(([t]) => t !== 'Personnalisé')
                  .map(([type, preset], i) => (
                    <tr key={type} className={i % 2 === 0 ? 'bg-surface-container-lowest' : 'bg-surface-container-low/30'}>
                      <td className="p-2.5 font-semibold text-on-surface">{type}</td>
                      <td className="p-2.5 text-center font-mono text-on-surface">{preset.depart_h1}</td>
                      <td className="p-2.5 text-center font-mono text-on-surface">{preset.retour_h1}</td>
                      <td className="p-2.5 text-center font-mono text-on-surface-variant">{preset.depart_h2 ?? '—'}</td>
                      <td className="p-2.5 text-center font-mono text-on-surface">{preset.retour_h2 ?? '—'}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {/* Equipe cards */}
          {Array.from({ length: numShifts }, (_, i) => (
            <ShiftCard
              key={i}
              index={i}
              shift={shifts[i] ?? EMPTY_SHIFT}
              onChange={(s) => updateShift(i, s)}
            />
          ))}
        </div>
      </Card>

      {/* Configuration */}
      <Card title={t('sites.form.section_config', 'Configuration')}>
        <div className="flex flex-col gap-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Input label={t('sites.form.working_days', 'Jours travailles')} value={workingDays} onChange={(e) => setWorkingDays(e.target.value)} placeholder="Lun-Ven" />
            <Input label={t('sites.form.days_per_week', 'Jours par semaine')} type="number" value={String(daysPerWeek)} onChange={(e) => setDaysPerWeek(parseInt(e.target.value, 10) || 5)} min="1" max="7" />
          </div>
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
