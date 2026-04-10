import { useState, useCallback, useMemo } from 'react';
import { computeDepotLayout } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  DepotLayoutRequest,
  DepotLayoutResponse,
  ChargerPosition,
} from '@/types/sotreg';
import { CHARGER_TYPES, CHARGER_LABELS } from '@/types/sotreg';

/* ── Constants ────────────────────────────────────────────────────────────── */

const SVG_PADDING = 4;
const ZONE_LABEL_FONT = 11;

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const numFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

function fmtArea(value: number): string {
  return `${numFmt.format(value)} m\u00B2`;
}

/* ── Area summary card ────────────────────────────────────────────────────── */

function AreaCard({
  label,
  icon,
  value,
  accent,
}: {
  label: string;
  icon: string;
  value: number;
  accent?: boolean;
}) {
  return (
    <div
      className={[
        'rounded-lg p-4 flex flex-col items-center gap-1.5',
        accent
          ? 'bg-primary/10 border border-primary/15'
          : 'bg-surface-container-low',
      ].join(' ')}
    >
      <span
        className={[
          'material-symbols-outlined text-xl',
          accent ? 'text-primary' : 'text-on-surface-variant',
        ].join(' ')}
      >
        {icon}
      </span>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
        {label}
      </p>
      <p
        className={[
          'font-sans text-lg font-semibold',
          accent ? 'text-primary' : 'text-on-surface',
        ].join(' ')}
      >
        {fmtArea(value)}
      </p>
    </div>
  );
}

/* ── SVG Zone rectangle ───────────────────────────────────────────────────── */

interface ZoneRectProps {
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
  stroke: string;
  label: string;
  areaM2: number;
}

function ZoneRect({
  x,
  y,
  width,
  height,
  fill,
  stroke,
  label,
  areaM2,
}: ZoneRectProps) {
  const cx = x + width / 2;
  const cy = y + height / 2;

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={fill}
        stroke={stroke}
        strokeWidth={1.5}
        rx={2}
      />
      <text
        x={cx}
        y={cy - 6}
        textAnchor="middle"
        dominantBaseline="central"
        fill={stroke}
        fontFamily="Inter, sans-serif"
        fontSize={ZONE_LABEL_FONT}
        fontWeight={600}
      >
        {label}
      </text>
      <text
        x={cx}
        y={cy + 10}
        textAnchor="middle"
        dominantBaseline="central"
        fill={stroke}
        fontFamily="Inter, sans-serif"
        fontSize={ZONE_LABEL_FONT - 2}
        fontWeight={400}
      >
        {fmtArea(areaM2)}
      </text>
    </g>
  );
}

/* ── SVG charger bay ──────────────────────────────────────────────────────── */

function ChargerBay({ pos }: { pos: ChargerPosition }) {
  return (
    <g>
      <rect
        x={pos.x}
        y={pos.y}
        width={pos.bay_width}
        height={pos.bay_depth}
        fill="#0058be"
        fillOpacity={0.55}
        stroke="#0058be"
        strokeWidth={1}
        rx={1}
      />
      <text
        x={pos.x + pos.bay_width / 2}
        y={pos.y + pos.bay_depth / 2}
        textAnchor="middle"
        dominantBaseline="central"
        fill="#fff"
        fontFamily="Inter, sans-serif"
        fontSize={8}
        fontWeight={600}
      >
        {pos.bay_id}
      </text>
    </g>
  );
}

/* ── Layout zones compute ─────────────────────────────────────────────────── */

interface LayoutZones {
  charging: { x: number; y: number; w: number; h: number };
  parking: { x: number; y: number; w: number; h: number };
  maintenance: { x: number; y: number; w: number; h: number } | null;
  circulation: { x: number; y: number; w: number; h: number };
}

function computeZones(data: DepotLayoutResponse): LayoutZones {
  const totalW = data.dimensions.width_m;
  const totalH = data.dimensions.depth_m;
  const totalArea = data.total_area_m2;

  const chargingRatio = data.charging_area_m2 / totalArea;
  const parkingRatio = data.parking_area_m2 / totalArea;
  const maintenanceRatio = data.maintenance_area_m2 / totalArea;
  const circulationRatio = data.circulation_area_m2 / totalArea;

  /* Horizontal strip layout: charging | parking | maintenance | circulation */
  let x = 0;

  const chargingW = totalW * chargingRatio;
  const charging = { x, y: 0, w: chargingW, h: totalH };
  x += chargingW;

  const parkingW = totalW * parkingRatio;
  const parking = { x, y: 0, w: parkingW, h: totalH };
  x += parkingW;

  let maintenance: LayoutZones['maintenance'] = null;
  if (data.maintenance_area_m2 > 0) {
    const maintW = totalW * maintenanceRatio;
    maintenance = { x, y: 0, w: maintW, h: totalH };
    x += maintW;
  }

  const circulationW = totalW * circulationRatio;
  const circulation = { x, y: 0, w: circulationW, h: totalH };

  /* Suppress unused variable warning */
  void circulationRatio;

  return { charging, parking, maintenance, circulation };
}

/* ── Main component ───────────────────────────────────────────────────────── */

export function DepotLayoutViewer() {
  /* Form state */
  const [chargerCount, setChargerCount] = useState(4);
  const [fleetSize, setFleetSize] = useState(10);
  const [chargerType, setChargerType] = useState<string>(CHARGER_TYPES[1]);
  const [includeMaintenance, setIncludeMaintenance] = useState(true);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DepotLayoutResponse | null>(null);

  /* ── Handlers ───────────────────────────────────────────────────────────── */

  const handleCompute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: DepotLayoutRequest = {
        charger_count: chargerCount,
        fleet_size: fleetSize,
        charger_type: chargerType,
        include_maintenance: includeMaintenance,
      };
      const res = await computeDepotLayout(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors de la planification du depot'));
    } finally {
      setLoading(false);
    }
  }, [chargerCount, fleetSize, chargerType, includeMaintenance]);

  /* ── Layout zones ───────────────────────────────────────────────────────── */

  const zones = useMemo(() => {
    if (!result) return null;
    return computeZones(result);
  }, [result]);

  const viewBox = useMemo(() => {
    if (!result) return '0 0 100 60';
    const w = result.dimensions.width_m + SVG_PADDING * 2;
    const h = result.dimensions.depth_m + SVG_PADDING * 2;
    return `${-SVG_PADDING} ${-SVG_PADDING} ${w} ${h}`;
  }, [result]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          warehouse
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Plan du depot
        </h3>
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
        {/* Charger count */}
        <div>
          <label
            htmlFor="depot-charger-count"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Nombre de chargeurs
          </label>
          <input
            id="depot-charger-count"
            type="number"
            min={1}
            max={100}
            value={chargerCount}
            onChange={(e) => setChargerCount(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Fleet size */}
        <div>
          <label
            htmlFor="depot-fleet-size"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Taille de la flotte
          </label>
          <input
            id="depot-fleet-size"
            type="number"
            min={1}
            max={5000}
            value={fleetSize}
            onChange={(e) => setFleetSize(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Charger type */}
        <div>
          <label
            htmlFor="depot-charger-type"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Type de chargeur
          </label>
          <select
            id="depot-charger-type"
            value={chargerType}
            onChange={(e) => setChargerType(e.target.value)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          >
            {CHARGER_TYPES.map((ct) => (
              <option key={ct} value={ct}>
                {CHARGER_LABELS[ct]}
              </option>
            ))}
          </select>
        </div>

        {/* Include maintenance */}
        <div className="flex items-end pb-1">
          <label className="inline-flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeMaintenance}
              onChange={(e) => setIncludeMaintenance(e.target.checked)}
              className="w-4 h-4 rounded border-outline-variant/30 text-primary focus:ring-primary/20 accent-primary"
            />
            <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
              Zone maintenance
            </span>
          </label>
        </div>
      </div>

      {/* Compute button */}
      <button
        type="button"
        onClick={handleCompute}
        disabled={loading}
        className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-base">
              progress_activity
            </span>
            Planification en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-base">
              grid_view
            </span>
            Planifier
          </>
        )}
      </button>

      {/* Error state */}
      {error && (
        <div className="mt-4 flex items-start gap-2 bg-error-container/30 text-error rounded-lg px-4 py-3">
          <span className="material-symbols-outlined text-base mt-0.5">
            error
          </span>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && zones && !loading && (
        <div className="mt-6 space-y-6">
          {/* Dimensions display */}
          <div className="flex items-center justify-center gap-3 py-2">
            <span className="material-symbols-outlined text-lg text-on-surface-variant">
              straighten
            </span>
            <p className="font-sans text-lg font-semibold text-on-surface">
              {numFmt.format(result.dimensions.width_m)} m{' '}
              <span className="text-on-surface-variant font-normal">&times;</span>{' '}
              {numFmt.format(result.dimensions.depth_m)} m
            </p>
            <span className="text-xs text-on-surface-variant">
              ({result.charger_count} chargeurs {CHARGER_LABELS[result.charger_type] ?? result.charger_type} | {result.parking_bays} places)
            </span>
          </div>

          {/* Area summary cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <AreaCard
              label="Surface totale"
              icon="square_foot"
              value={result.total_area_m2}
              accent
            />
            <AreaCard
              label="Zone recharge"
              icon="ev_charger"
              value={result.charging_area_m2}
            />
            <AreaCard
              label="Zone parking"
              icon="local_parking"
              value={result.parking_area_m2}
            />
            <AreaCard
              label="Zone maintenance"
              icon="build"
              value={result.maintenance_area_m2}
            />
            <AreaCard
              label="Circulation"
              icon="route"
              value={result.circulation_area_m2}
            />
          </div>

          {/* SVG layout visualization */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Vue du plan
            </p>
            <div className="bg-surface-container rounded-lg p-4 border border-outline-variant/10">
              <svg
                width="100%"
                viewBox={viewBox}
                className="font-sans"
                role="img"
                aria-label="Plan du depot avec zones de recharge, parking, maintenance et circulation"
              >
                {/* Outer depot boundary */}
                <rect
                  x={0}
                  y={0}
                  width={result.dimensions.width_m}
                  height={result.dimensions.depth_m}
                  fill="none"
                  stroke="#424754"
                  strokeWidth={1.5}
                  strokeDasharray="4 2"
                  rx={2}
                />

                {/* Charging zone */}
                <ZoneRect
                  x={zones.charging.x}
                  y={zones.charging.y}
                  width={zones.charging.w}
                  height={zones.charging.h}
                  fill="rgba(0, 88, 190, 0.20)"
                  stroke="#0058be"
                  label="Recharge"
                  areaM2={result.charging_area_m2}
                />

                {/* Charger bay positions */}
                {result.charger_positions.map((pos) => (
                  <ChargerBay key={pos.bay_id} pos={pos} />
                ))}

                {/* Parking zone */}
                <ZoneRect
                  x={zones.parking.x}
                  y={zones.parking.y}
                  width={zones.parking.w}
                  height={zones.parking.h}
                  fill="rgba(148, 163, 184, 0.20)"
                  stroke="#64748b"
                  label="Parking"
                  areaM2={result.parking_area_m2}
                />

                {/* Maintenance zone */}
                {zones.maintenance && result.maintenance_area_m2 > 0 && (
                  <ZoneRect
                    x={zones.maintenance.x}
                    y={zones.maintenance.y}
                    width={zones.maintenance.w}
                    height={zones.maintenance.h}
                    fill="rgba(245, 158, 11, 0.20)"
                    stroke="#d97706"
                    label="Maintenance"
                    areaM2={result.maintenance_area_m2}
                  />
                )}

                {/* Circulation zone */}
                <ZoneRect
                  x={zones.circulation.x}
                  y={zones.circulation.y}
                  width={zones.circulation.w}
                  height={zones.circulation.h}
                  fill="rgba(226, 232, 240, 0.30)"
                  stroke="#94a3b8"
                  label="Circulation"
                  areaM2={result.circulation_area_m2}
                />
              </svg>
            </div>
          </div>

          {/* Legend */}
          <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-on-surface-variant">
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded-sm" style={{ background: 'rgba(0, 88, 190, 0.35)' }} />
              Recharge
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded-sm bg-slate-300/50" />
              Parking
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded-sm" style={{ background: 'rgba(245, 158, 11, 0.35)' }} />
              Maintenance
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded-sm bg-slate-200/50" />
              Circulation
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded-sm bg-primary/55" />
              Borne
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="mt-6 flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            warehouse
          </span>
          <p className="text-sm">
            Configurez les parametres et cliquez sur Planifier pour generer le plan du depot.
          </p>
        </div>
      )}
    </div>
  );
}
