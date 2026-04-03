import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { getSettings, updateSettings } from '@/api/settings';
import { extractApiError } from '@/lib/apiError';
import { Button } from '@/components/ui/Button';
import { ShiftsEditorTable } from '@/components/shifts/ShiftsEditorTable';
import type { OptimizationSettings } from '@/types/settings';

interface FieldConfig {
  key: keyof OptimizationSettings;
  labelKey: string;
  defaultLabel: string;
  type: 'number' | 'range' | 'time';
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
}

const OPTIMIZATION_FIELDS: FieldConfig[] = [
  {
    key: 'meeting_radius_meters',
    labelKey: 'settings.meeting_radius',
    defaultLabel: 'Rayon de rencontre (m)',
    type: 'range',
    min: 50,
    max: 5000,
    step: 50,
    unit: 'm',
  },
  {
    key: 'max_walking_distance_meters',
    labelKey: 'settings.max_walking_distance',
    defaultLabel: 'Distance de marche max (m)',
    type: 'range',
    min: 100,
    max: 5000,
    step: 50,
    unit: 'm',
  },
  {
    key: 'max_route_duration_seconds',
    labelKey: 'settings.max_route_duration',
    defaultLabel: 'Duree max de trajet (s)',
    type: 'range',
    min: 600,
    max: 18000,
    step: 60,
    unit: 's',
  },
];

const COST_FIELDS: FieldConfig[] = [
  {
    key: 'fuel_cost_per_liter',
    labelKey: 'settings.fuel_cost',
    defaultLabel: 'Cout du carburant (MAD/L)',
    type: 'number',
    min: 0,
    step: 0.01,
    unit: 'MAD/L',
  },
  {
    key: 'fuel_consumption_l_per_100km',
    labelKey: 'settings.fuel_consumption',
    defaultLabel: 'Consommation (L/100km)',
    type: 'number',
    min: 0,
    step: 0.1,
    unit: 'L/100km',
  },
  {
    key: 'co2_kg_per_liter',
    labelKey: 'settings.co2_per_liter',
    defaultLabel: 'CO2 par litre (kg/L)',
    type: 'number',
    min: 0,
    step: 0.01,
    unit: 'kg/L',
  },
];

const RTI_FIELDS: FieldConfig[] = [
  {
    key: 'rti_threshold_minutes',
    labelKey: 'settings.rti_threshold',
    defaultLabel: 'Seuil RTI (min)',
    type: 'number',
    min: 1,
    max: 120,
    step: 1,
    unit: 'min',
  },
];

const NIGHT_FIELDS_TIME: FieldConfig[] = [
  {
    key: 'night_mode_start',
    labelKey: 'settings.night_start',
    defaultLabel: 'Debut mode nuit',
    type: 'time',
  },
  {
    key: 'night_mode_end',
    labelKey: 'settings.night_end',
    defaultLabel: 'Fin mode nuit',
    type: 'time',
  },
];

const NIGHT_FIELDS_NUMBER: FieldConfig[] = [
  {
    key: 'min_night_group_size',
    labelKey: 'settings.min_night_group',
    defaultLabel: 'Taille min. groupe nuit',
    type: 'number',
    min: 1,
    max: 50,
    step: 1,
  },
];

type FormValues = Record<string, string | number>;

function extractFormValues(settings: OptimizationSettings): FormValues {
  return {
    meeting_radius_meters: settings.meeting_radius_meters,
    max_walking_distance_meters: settings.max_walking_distance_meters,
    max_route_duration_seconds: settings.max_route_duration_seconds,
    fuel_cost_per_liter: settings.fuel_cost_per_liter,
    fuel_consumption_l_per_100km: settings.fuel_consumption_l_per_100km,
    co2_kg_per_liter: settings.co2_kg_per_liter,
    rti_threshold_minutes: settings.rti_threshold_minutes,
    night_mode_start: settings.night_mode_start,
    night_mode_end: settings.night_mode_end,
    min_night_group_size: settings.min_night_group_size,
  };
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-sm font-bold uppercase tracking-widest text-on-surface-variant mb-4">
      {children}
    </h2>
  );
}

export function SettingsPage() {
  const { t } = useTranslation();

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [formValues, setFormValues] = useState<FormValues>({});
  const [originalSettings, setOriginalSettings] =
    useState<OptimizationSettings | null>(null);

  const loadSettings = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getSettings();
      setOriginalSettings(data);
      setFormValues(extractFormValues(data));
    } catch (err: unknown) {
      setError(extractApiError(err, t('common.error', 'Une erreur est survenue')));
    } finally {
      setIsLoading(false);
    }
  }, [t]);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const handleChange = useCallback(
    (key: string, value: string | number) => {
      setFormValues((prev) => ({ ...prev, [key]: value }));
      if (successMsg) setSuccessMsg(null);
    },
    [successMsg],
  );

  const handleSave = useCallback(async () => {
    if (!originalSettings) return;

    const changedFields: Record<string, unknown> = {};
    const original = extractFormValues(originalSettings);

    for (const [key, value] of Object.entries(formValues)) {
      if (String(value) !== String(original[key])) {
        changedFields[key] = value;
      }
    }

    if (Object.keys(changedFields).length === 0) {
      setSuccessMsg(
        t('settings.no_changes', 'Aucune modification a enregistrer.'),
      );
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccessMsg(null);
      const updated = await updateSettings(
        changedFields as Partial<OptimizationSettings>,
      );
      setOriginalSettings(updated);
      setFormValues(extractFormValues(updated));
      setSuccessMsg(
        t('settings.save_success', 'Parametres enregistres avec succes.'),
      );
    } catch (err: unknown) {
      setError(extractApiError(err, t('common.error', 'Une erreur est survenue')));
    } finally {
      setIsSaving(false);
    }
  }, [originalSettings, formValues, t]);

  const renderField = useCallback(
    (field: FieldConfig) => {
      const value = formValues[field.key] ?? '';

      if (field.type === 'range') {
        return (
          <div key={field.key} className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <label className="text-[10px] font-bold uppercase tracking-widest text-outline">
                {t(field.labelKey, field.defaultLabel)}
              </label>
              <span className="text-sm font-sans font-medium text-on-surface tabular-nums">
                {value}
                {field.unit ? ` ${field.unit}` : ''}
              </span>
            </div>
            <input
              type="range"
              min={field.min}
              max={field.max}
              step={field.step}
              value={value}
              onChange={(e) =>
                handleChange(field.key, parseFloat(e.target.value))
              }
              className="w-full h-2 rounded-lg appearance-none cursor-pointer accent-primary bg-surface-container-high"
            />
            <div className="flex items-center justify-between text-[10px] font-sans text-on-surface-variant">
              <span>
                {field.min}
                {field.unit ? ` ${field.unit}` : ''}
              </span>
              <span>
                {field.max}
                {field.unit ? ` ${field.unit}` : ''}
              </span>
            </div>
          </div>
        );
      }

      if (field.type === 'time') {
        return (
          <div key={field.key} className="flex flex-col gap-1.5">
            <label className="text-[10px] font-bold uppercase tracking-widest text-outline">
              {t(field.labelKey, field.defaultLabel)}
            </label>
            <input
              type="time"
              value={value}
              onChange={(e) => handleChange(field.key, e.target.value)}
              className="bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
        );
      }

      // number
      return (
        <div key={field.key} className="flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-widest text-outline">
            {t(field.labelKey, field.defaultLabel)}
          </label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={field.min}
              max={field.max}
              step={field.step}
              value={value}
              onChange={(e) =>
                handleChange(field.key, parseFloat(e.target.value) || 0)
              }
              className="flex-1 bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none focus:ring-2 focus:ring-primary/20"
            />
            {field.unit && (
              <span className="text-xs font-sans text-on-surface-variant whitespace-nowrap">
                {field.unit}
              </span>
            )}
          </div>
        </div>
      );
    },
    [formValues, handleChange, t],
  );

  // Loading state
  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <svg
            className="animate-spin h-8 w-8 text-primary"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <span className="text-sm font-sans text-on-surface-variant">
            {t('common.loading', 'Chargement...')}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-sans text-3xl font-black tracking-tight text-on-surface">
          {t('settings.title', 'Parametres')}
        </h1>
        <Button
          variant="primary"
          size="md"
          isLoading={isSaving}
          onClick={handleSave}
        >
          {t('common.save', 'Enregistrer')}
        </Button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-error-container rounded-xl p-4 mb-4 flex items-center justify-between">
          <p className="text-error text-sm font-sans">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-error text-sm font-sans font-medium hover:underline ml-4 cursor-pointer"
          >
            {t('common.dismiss', 'Fermer')}
          </button>
        </div>
      )}

      {/* Success banner */}
      {successMsg && (
        <div className="bg-green-50 rounded-xl p-4 mb-4 flex items-center justify-between">
          <p className="text-green-700 text-sm font-sans">
            {successMsg}
          </p>
          <button
            onClick={() => setSuccessMsg(null)}
            className="text-green-700 text-sm font-sans font-medium hover:underline ml-4 cursor-pointer"
          >
            {t('common.dismiss', 'Fermer')}
          </button>
        </div>
      )}

      {/* Form */}
      <div className="flex flex-col gap-6 pb-8">
        {/* Shifts */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <SectionHeading>
            Shifts
          </SectionHeading>
          <ShiftsEditorTable siteId={null} />
        </div>

        {/* Optimization Parameters */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <SectionHeading>
            {t('settings.section_optimization', 'Parametres d\'optimisation')}
          </SectionHeading>
          <div className="flex flex-col gap-6">
            {OPTIMIZATION_FIELDS.map(renderField)}
          </div>
        </div>

        {/* Cost Parameters */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <SectionHeading>
            {t('settings.section_cost', 'Parametres de cout')}
          </SectionHeading>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {COST_FIELDS.map(renderField)}
          </div>
        </div>

        {/* RTI */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <SectionHeading>
            {t('settings.section_rti', 'Information Temps Reel (RTI)')}
          </SectionHeading>
          <div className="max-w-xs">{RTI_FIELDS.map(renderField)}</div>
        </div>

        {/* Night Mode */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <SectionHeading>
            {t('settings.section_night', 'Mode Nuit')}
          </SectionHeading>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {NIGHT_FIELDS_TIME.map(renderField)}
            {NIGHT_FIELDS_NUMBER.map(renderField)}
          </div>
        </div>

        {/* Bottom save button */}
        <div className="flex justify-end">
          <Button
            variant="primary"
            size="md"
            isLoading={isSaving}
            onClick={handleSave}
          >
            {t('common.save', 'Enregistrer')}
          </Button>
        </div>
      </div>
    </div>
  );
}
