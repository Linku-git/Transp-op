import { useState, useEffect, useCallback, useMemo, type FormEvent } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { APIProvider, Map, AdvancedMarker } from '@vis.gl/react-google-maps';
import type { MapMouseEvent } from '@vis.gl/react-google-maps';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { extractApiError } from '@/lib/apiError';
import { createLigne, updateLigne, getLigne } from '@/api/sotreg';
import type { Ligne, LigneCreate, LigneUpdate } from '@/types/sotreg';
import {
  SERVICE_TYPE_OPTIONS,
  SERVICE_TYPE_LABELS,
  MOTORIZATION_OPTIONS,
  MOTORIZATION_LABELS,
} from '@/types/sotreg';

/* ── Constants ──────────────────────────────────────────────────────────── */

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '';
const CASABLANCA = { lat: 33.5731, lng: -7.5898 };
const DEFAULT_ZOOM = 11;

/* ── Helpers ────────────────────────────────────────────────────────────── */

interface FieldErrors {
  [field: string]: string;
}

function SelectField({
  label,
  value,
  onChange,
  options,
  error,
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
  error?: string;
  required?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
        {label}
        {required && ' *'}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={[
          'w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm',
          'outline-none transition-shadow duration-150 appearance-none',
          error
            ? 'ring-2 ring-error/40'
            : 'focus:ring-2 focus:ring-primary/20',
        ].join(' ')}
      >
        <option value="">-- Choisir --</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
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

function ReadonlyField({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
        {label}
      </label>
      <div className="w-full bg-surface-container/60 rounded-lg p-3 text-on-surface-variant font-sans text-sm tabular-nums">
        {value}
      </div>
    </div>
  );
}

/* ── Main Component ─────────────────────────────────────────────────────── */

export function LigneFormPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditMode = Boolean(id);

  /* ── Form state ───────────────────────────────────────────────────────── */

  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [serviceType, setServiceType] = useState('');
  const [siteId, setSiteId] = useState('');

  const [originLat, setOriginLat] = useState<number>(CASABLANCA.lat);
  const [originLng, setOriginLng] = useState<number>(CASABLANCA.lng);
  const [destLat, setDestLat] = useState<number>(CASABLANCA.lat + 0.02);
  const [destLng, setDestLng] = useState<number>(CASABLANCA.lng + 0.02);

  const [distanceKm, setDistanceKm] = useState<number>(0);
  const [rotationsPerDay, setRotationsPerDay] = useState<number>(1);
  const [operatingDaysPerYear, setOperatingDaysPerYear] = useState<number>(250);

  const [vehicleType, setVehicleType] = useState('');
  const [motorization, setMotorization] = useState('');
  const [passengerCountAvg, setPassengerCountAvg] = useState('');
  const [shiftType, setShiftType] = useState('');
  const [penteMoyennePct, setPenteMoyennePct] = useState('');

  /* ── UI state ─────────────────────────────────────────────────────────── */

  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [existingLigne, setExistingLigne] = useState<Ligne | null>(null);

  // Map click toggle: 'origin' | 'destination'
  const [mapClickTarget, setMapClickTarget] = useState<'origin' | 'destination'>('origin');

  /* ── Computed km_annual ───────────────────────────────────────────────── */

  const kmAnnual = useMemo(
    () => distanceKm * rotationsPerDay * operatingDaysPerYear,
    [distanceKm, rotationsPerDay, operatingDaysPerYear],
  );

  /* ── Load existing ligne for edit mode ────────────────────────────────── */

  useEffect(() => {
    if (!id) return;
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setApiError(null);
      try {
        const ligne = await getLigne(id as string);
        if (cancelled) return;
        setExistingLigne(ligne);

        setCode(ligne.code);
        setName(ligne.name);
        setServiceType(ligne.service_type);
        setSiteId(ligne.site_id ?? '');

        setOriginLat(ligne.origin_lat);
        setOriginLng(ligne.origin_lng);
        setDestLat(ligne.dest_lat);
        setDestLng(ligne.dest_lng);

        setDistanceKm(ligne.distance_km);
        setRotationsPerDay(ligne.rotations_per_day);
        setOperatingDaysPerYear(ligne.operating_days_per_year);

        setVehicleType(ligne.vehicle_type ?? '');
        setMotorization(ligne.motorization ?? '');
        setPassengerCountAvg(
          ligne.passenger_count_avg != null ? String(ligne.passenger_count_avg) : '',
        );
        setShiftType(ligne.shift_type ?? '');
        setPenteMoyennePct(
          ligne.pente_moyenne_pct != null ? String(ligne.pente_moyenne_pct) : '',
        );
      } catch (err: unknown) {
        if (!cancelled) {
          setApiError(extractApiError(err, 'Impossible de charger la ligne'));
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  /* ── Validation ───────────────────────────────────────────────────────── */

  const validate = useCallback((): boolean => {
    const e: FieldErrors = {};

    if (!isEditMode && !code.trim()) e.code = 'Ce champ est requis';
    if (!isEditMode && code.trim().length > 20)
      e.code = 'Maximum 20 caracteres';
    if (!name.trim()) e.name = 'Ce champ est requis';
    if (!serviceType) e.serviceType = 'Ce champ est requis';

    if (originLat < -90 || originLat > 90)
      e.originLat = 'Latitude entre -90 et 90';
    if (originLng < -180 || originLng > 180)
      e.originLng = 'Longitude entre -180 et 180';
    if (destLat < -90 || destLat > 90)
      e.destLat = 'Latitude entre -90 et 90';
    if (destLng < -180 || destLng > 180)
      e.destLng = 'Longitude entre -180 et 180';

    if (distanceKm <= 0) e.distanceKm = 'Doit etre superieur a 0';
    if (rotationsPerDay < 1) e.rotationsPerDay = 'Minimum 1';
    if (operatingDaysPerYear < 1 || operatingDaysPerYear > 366)
      e.operatingDaysPerYear = 'Entre 1 et 366';

    setErrors(e);
    return Object.keys(e).length === 0;
  }, [
    isEditMode,
    code,
    name,
    serviceType,
    originLat,
    originLng,
    destLat,
    destLng,
    distanceKm,
    rotationsPerDay,
    operatingDaysPerYear,
  ]);

  /* ── Submit ───────────────────────────────────────────────────────────── */

  const handleSubmit = useCallback(
    async (ev: FormEvent) => {
      ev.preventDefault();
      if (!validate()) return;

      setIsSubmitting(true);
      setApiError(null);

      try {
        if (isEditMode && id) {
          const data: LigneUpdate = {
            name: name.trim(),
            service_type: serviceType,
            site_id: siteId.trim() || null,
            origin_lat: originLat,
            origin_lng: originLng,
            dest_lat: destLat,
            dest_lng: destLng,
            distance_km: distanceKm,
            rotations_per_day: rotationsPerDay,
            operating_days_per_year: operatingDaysPerYear,
            vehicle_type: vehicleType.trim() || null,
            motorization: motorization || null,
            passenger_count_avg: passengerCountAvg
              ? Number(passengerCountAvg)
              : null,
            shift_type: shiftType.trim() || null,
            pente_moyenne_pct: penteMoyennePct
              ? Number(penteMoyennePct)
              : null,
          };
          await updateLigne(id, data);
        } else {
          const data: LigneCreate = {
            code: code.trim(),
            name: name.trim(),
            service_type: serviceType,
            site_id: siteId.trim() || null,
            origin_lat: originLat,
            origin_lng: originLng,
            dest_lat: destLat,
            dest_lng: destLng,
            distance_km: distanceKm,
            rotations_per_day: rotationsPerDay,
            operating_days_per_year: operatingDaysPerYear,
            vehicle_type: vehicleType.trim() || null,
            motorization: motorization || null,
            passenger_count_avg: passengerCountAvg
              ? Number(passengerCountAvg)
              : null,
            shift_type: shiftType.trim() || null,
            pente_moyenne_pct: penteMoyennePct
              ? Number(penteMoyennePct)
              : null,
          };
          await createLigne(data);
        }
        navigate('/sotreg/lignes');
      } catch (err: unknown) {
        setApiError(extractApiError(err, 'Erreur lors de l\'enregistrement'));
      } finally {
        setIsSubmitting(false);
      }
    },
    [
      validate,
      isEditMode,
      id,
      code,
      name,
      serviceType,
      siteId,
      originLat,
      originLng,
      destLat,
      destLng,
      distanceKm,
      rotationsPerDay,
      operatingDaysPerYear,
      vehicleType,
      motorization,
      passengerCountAvg,
      shiftType,
      penteMoyennePct,
      navigate,
    ],
  );

  /* ── Map click handler ────────────────────────────────────────────────── */

  const handleMapClick = useCallback(
    (e: MapMouseEvent) => {
      if (!e.detail.latLng) return;
      const lat = Math.round(e.detail.latLng.lat * 1_000_000) / 1_000_000;
      const lng = Math.round(e.detail.latLng.lng * 1_000_000) / 1_000_000;

      if (mapClickTarget === 'origin') {
        setOriginLat(lat);
        setOriginLng(lng);
        setMapClickTarget('destination');
      } else {
        setDestLat(lat);
        setDestLng(lng);
        setMapClickTarget('origin');
      }
    },
    [mapClickTarget],
  );

  /* ── Map center ───────────────────────────────────────────────────────── */

  const mapCenter = useMemo(() => {
    const centerLat = (originLat + destLat) / 2;
    const centerLng = (originLng + destLng) / 2;
    return {
      lat: isNaN(centerLat) ? CASABLANCA.lat : centerLat,
      lng: isNaN(centerLng) ? CASABLANCA.lng : centerLng,
    };
  }, [originLat, originLng, destLat, destLng]);

  /* ── Loading state ────────────────────────────────────────────────────── */

  if (isEditMode && isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton variant="text" className="w-64 h-8" />
        <Skeleton variant="rectangular" className="w-full" height="200px" />
        <Skeleton variant="rectangular" className="w-full" height="300px" />
        <Skeleton variant="rectangular" className="w-full" height="200px" />
      </div>
    );
  }

  /* ── Not found state (edit mode but no data) ──────────────────────────── */

  if (isEditMode && !isLoading && !existingLigne && apiError) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3">
        <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">
          error
        </span>
        <p className="font-sans text-lg font-semibold text-on-surface">
          {apiError}
        </p>
        <Link
          to="/sotreg/lignes"
          className="text-sm text-primary font-sans hover:underline"
        >
          Retour a la liste des lignes
        </Link>
      </div>
    );
  }

  /* ── Page title ───────────────────────────────────────────────────────── */

  const pageTitle = isEditMode
    ? `Modifier Ligne: ${existingLigne?.code ?? ''}`
    : 'Nouvelle Ligne';

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <Link
          to="/sotreg/lignes"
          className="inline-flex items-center gap-1 text-sm text-primary font-sans hover:underline mb-4"
        >
          <span className="material-symbols-outlined text-base">
            arrow_back
          </span>
          Retour aux lignes
        </Link>
        <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight">
          {pageTitle}
        </h1>
        {isEditMode && existingLigne && (
          <p className="text-sm text-on-surface-variant font-sans mt-1">
            {existingLigne.name} &mdash; {existingLigne.code}
          </p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-8" noValidate>
        {/* API error banner */}
        {apiError && !isLoading && (
          <div className="bg-error-container/30 rounded-xl p-4 flex items-center gap-3">
            <span className="material-symbols-outlined text-error text-lg">
              error
            </span>
            <p className="text-error text-sm font-sans">{apiError}</p>
          </div>
        )}

        {/* ── Section: Identification ───────────────────────────────────── */}
        <Card title="Identification">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {isEditMode ? (
              <ReadonlyField label="Code" value={code} />
            ) : (
              <Input
                label="Code *"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                error={errors.code}
                placeholder="L-001"
                maxLength={20}
              />
            )}
            <Input
              label="Nom *"
              value={name}
              onChange={(e) => setName(e.target.value)}
              error={errors.name}
              placeholder="Ligne Casablanca - Mohammedia"
            />
            <SelectField
              label="Type de service"
              value={serviceType}
              onChange={setServiceType}
              options={SERVICE_TYPE_OPTIONS.map((v) => ({
                value: v,
                label: SERVICE_TYPE_LABELS[v] ?? v,
              }))}
              error={errors.serviceType}
              required
            />
            <Input
              label="Site ID"
              value={siteId}
              onChange={(e) => setSiteId(e.target.value)}
              placeholder="UUID du site (optionnel)"
            />
          </div>
        </Card>

        {/* ── Section: Geographie ───────────────────────────────────────── */}
        <Card title="Geographie">
          <div className="flex flex-col gap-5">
            {/* Origin / Destination coords */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Origin */}
              <div className="flex flex-col gap-3">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-bold"
                    style={{ backgroundColor: '#0058be' }}
                  >
                    O
                  </span>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
                    Origine
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="Latitude"
                    type="number"
                    value={String(originLat)}
                    onChange={(e) =>
                      setOriginLat(parseFloat(e.target.value) || 0)
                    }
                    error={errors.originLat}
                    step="0.000001"
                    min="-90"
                    max="90"
                  />
                  <Input
                    label="Longitude"
                    type="number"
                    value={String(originLng)}
                    onChange={(e) =>
                      setOriginLng(parseFloat(e.target.value) || 0)
                    }
                    error={errors.originLng}
                    step="0.000001"
                    min="-180"
                    max="180"
                  />
                </div>
              </div>

              {/* Destination */}
              <div className="flex flex-col gap-3">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-bold"
                    style={{ backgroundColor: '#ba1a1a' }}
                  >
                    D
                  </span>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
                    Destination
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="Latitude"
                    type="number"
                    value={String(destLat)}
                    onChange={(e) =>
                      setDestLat(parseFloat(e.target.value) || 0)
                    }
                    error={errors.destLat}
                    step="0.000001"
                    min="-90"
                    max="90"
                  />
                  <Input
                    label="Longitude"
                    type="number"
                    value={String(destLng)}
                    onChange={(e) =>
                      setDestLng(parseFloat(e.target.value) || 0)
                    }
                    error={errors.destLng}
                    step="0.000001"
                    min="-180"
                    max="180"
                  />
                </div>
              </div>
            </div>

            {/* Map click target toggle */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-on-surface-variant font-sans">
                Cliquer sur la carte pour placer :
              </span>
              <button
                type="button"
                onClick={() => setMapClickTarget('origin')}
                className={[
                  'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-sans font-semibold transition-all',
                  mapClickTarget === 'origin'
                    ? 'bg-primary/10 text-primary ring-1 ring-primary/30'
                    : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high',
                ].join(' ')}
              >
                <span
                  className="inline-block w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: '#0058be' }}
                />
                Origine
              </button>
              <button
                type="button"
                onClick={() => setMapClickTarget('destination')}
                className={[
                  'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-sans font-semibold transition-all',
                  mapClickTarget === 'destination'
                    ? 'bg-error/10 text-error ring-1 ring-error/30'
                    : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high',
                ].join(' ')}
              >
                <span
                  className="inline-block w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: '#ba1a1a' }}
                />
                Destination
              </button>
            </div>

            {/* Map */}
            <div className="rounded-xl overflow-hidden border border-outline-variant/10">
              <APIProvider apiKey={GOOGLE_MAPS_API_KEY} region="MA">
                <Map
                  center={mapCenter}
                  zoom={DEFAULT_ZOOM}
                  mapId="LIGNE_FORM_MAP"
                  streetViewControl={false}
                  mapTypeControl={false}
                  fullscreenControl={false}
                  gestureHandling="auto"
                  style={{ height: '380px', width: '100%' }}
                  onClick={handleMapClick}
                >
                  {/* Origin marker (blue) */}
                  <AdvancedMarker
                    position={{ lat: originLat, lng: originLng }}
                  >
                    <div className="flex flex-col items-center">
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-lg"
                        style={{ backgroundColor: '#0058be' }}
                      >
                        O
                      </div>
                      <div
                        className="w-0 h-0"
                        style={{
                          borderLeft: '6px solid transparent',
                          borderRight: '6px solid transparent',
                          borderTop: '8px solid #0058be',
                        }}
                      />
                    </div>
                  </AdvancedMarker>

                  {/* Destination marker (red) */}
                  <AdvancedMarker position={{ lat: destLat, lng: destLng }}>
                    <div className="flex flex-col items-center">
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-lg"
                        style={{ backgroundColor: '#ba1a1a' }}
                      >
                        D
                      </div>
                      <div
                        className="w-0 h-0"
                        style={{
                          borderLeft: '6px solid transparent',
                          borderRight: '6px solid transparent',
                          borderTop: '8px solid #ba1a1a',
                        }}
                      />
                    </div>
                  </AdvancedMarker>
                </Map>
              </APIProvider>
            </div>

            <p className="text-xs text-on-surface-variant font-sans">
              Cliquez sur la carte pour definir l'origine (bleu) et la
              destination (rouge). Le prochain clic placera :{' '}
              <span className="font-bold">
                {mapClickTarget === 'origin' ? 'Origine' : 'Destination'}
              </span>
            </p>
          </div>
        </Card>

        {/* ── Section: Parametres operationnels ─────────────────────────── */}
        <Card title="Parametres operationnels">
          <div className="flex flex-col gap-5">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <Input
                label="Distance (km) *"
                type="number"
                value={String(distanceKm)}
                onChange={(e) =>
                  setDistanceKm(parseFloat(e.target.value) || 0)
                }
                error={errors.distanceKm}
                step="0.1"
                min="0.1"
              />
              <Input
                label="Rotations / jour *"
                type="number"
                value={String(rotationsPerDay)}
                onChange={(e) =>
                  setRotationsPerDay(parseInt(e.target.value, 10) || 1)
                }
                error={errors.rotationsPerDay}
                min="1"
                step="1"
              />
              <Input
                label="Jours / an *"
                type="number"
                value={String(operatingDaysPerYear)}
                onChange={(e) =>
                  setOperatingDaysPerYear(parseInt(e.target.value, 10) || 1)
                }
                error={errors.operatingDaysPerYear}
                min="1"
                max="366"
                step="1"
              />
            </div>

            {/* Computed km_annual */}
            <div className="bg-surface-container-low/50 rounded-xl p-4 flex items-center gap-4">
              <span className="material-symbols-outlined text-primary text-xl">
                calculate
              </span>
              <div className="flex flex-col">
                <span className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
                  Km annuels (calcule)
                </span>
                <span className="text-lg font-black text-on-surface font-sans tabular-nums">
                  {kmAnnual.toLocaleString('fr-FR', {
                    maximumFractionDigits: 1,
                  })}{' '}
                  km
                </span>
              </div>
              <span className="text-[10px] text-on-surface-variant font-sans ml-auto">
                = distance x rotations x jours
              </span>
            </div>
          </div>
        </Card>

        {/* ── Section: Vehicule ─────────────────────────────────────────── */}
        <Card title="Vehicule">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Input
              label="Type de vehicule"
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value)}
              placeholder="Bus, Minibus, Van..."
            />
            <SelectField
              label="Motorisation"
              value={motorization}
              onChange={setMotorization}
              options={MOTORIZATION_OPTIONS.map((v) => ({
                value: v,
                label: MOTORIZATION_LABELS[v] ?? v,
              }))}
            />
            <Input
              label="Passagers moyens"
              type="number"
              value={passengerCountAvg}
              onChange={(e) => setPassengerCountAvg(e.target.value)}
              placeholder="Ex: 35"
              min="0"
            />
            <Input
              label="Type de shift"
              value={shiftType}
              onChange={(e) => setShiftType(e.target.value)}
              placeholder="Matin, Soir, Mixte..."
            />
            <Input
              label="Pente moyenne (%)"
              type="number"
              value={penteMoyennePct}
              onChange={(e) => setPenteMoyennePct(e.target.value)}
              placeholder="Ex: 3.5"
              step="0.1"
            />
          </div>
        </Card>

        {/* ── Action buttons ────────────────────────────────────────────── */}
        <div className="flex items-center gap-4 justify-end">
          <Button
            variant="ghost"
            type="button"
            onClick={() => navigate('/sotreg/lignes')}
          >
            Annuler
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            <span className="material-symbols-outlined text-base mr-1.5">
              save
            </span>
            Enregistrer
          </Button>
        </div>
      </form>
    </div>
  );
}
