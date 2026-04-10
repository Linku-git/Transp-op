import { useMemo } from 'react';
import type { PhaseResult } from '@/types/sotreg';
import { WAVE_COLORS } from '@/types/sotreg';

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

function fmtMAD(value: number): string {
  return `${madFmt.format(value)} MAD`;
}

/* ── Layout constants ─────────────────────────────────────────────────────── */

const ROW_HEIGHT = 52;
const ROW_GAP = 8;
const LABEL_WIDTH = 180;
const AXIS_HEIGHT = 32;
const PADDING_RIGHT = 24;
const PADDING_TOP = 8;
const BAR_RADIUS = 6;

/* ── Main component ───────────────────────────────────────────────────────── */

export function GanttChart({ phases }: { phases: PhaseResult[] }) {
  /* Compute year range across all phases */
  const { minYear, maxYear, years } = useMemo(() => {
    if (phases.length === 0) {
      return { minYear: 2026, maxYear: 2036, years: [] as number[] };
    }
    const mn = Math.min(...phases.map((p) => p.start_year));
    const mx = Math.max(...phases.map((p) => p.end_year));
    const yrs: number[] = [];
    for (let y = mn; y <= mx; y++) {
      yrs.push(y);
    }
    return { minYear: mn, maxYear: mx, years: yrs };
  }, [phases]);

  const yearSpan = maxYear - minYear || 1;
  const chartWidth = 600;
  const barAreaWidth = chartWidth - LABEL_WIDTH - PADDING_RIGHT;
  const svgHeight =
    PADDING_TOP +
    AXIS_HEIGHT +
    phases.length * (ROW_HEIGHT + ROW_GAP) +
    ROW_GAP;

  /* Convert year to x position in the bar area */
  const yearToX = (year: number): number => {
    return LABEL_WIDTH + ((year - minYear) / yearSpan) * barAreaWidth;
  };

  if (phases.length === 0) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <div className="flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            timeline
          </span>
          <p className="text-sm">Aucune phase a afficher.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          view_timeline
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Diagramme de Gantt
        </h3>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mb-4">
        {Object.entries(WAVE_COLORS).map(([wave, color]) => (
          <div key={wave} className="flex items-center gap-1.5">
            <span
              className="inline-block w-3 h-3 rounded-sm"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs text-on-surface-variant capitalize">
              {wave}
            </span>
          </div>
        ))}
      </div>

      {/* SVG Gantt chart */}
      <div className="overflow-x-auto">
        <svg
          width={chartWidth}
          height={svgHeight}
          viewBox={`0 0 ${chartWidth} ${svgHeight}`}
          className="min-w-full"
          role="img"
          aria-label="Diagramme de Gantt des phases de transition"
        >
          {/* ── Year axis ───────────────────────────────────────────────── */}
          {years.map((year) => {
            const x = yearToX(year);
            return (
              <g key={year}>
                {/* Vertical grid line */}
                <line
                  x1={x}
                  y1={PADDING_TOP + AXIS_HEIGHT}
                  x2={x}
                  y2={svgHeight}
                  stroke="#c2c6d6"
                  strokeOpacity={0.2}
                  strokeDasharray="4 4"
                />
                {/* Year label */}
                <text
                  x={x}
                  y={PADDING_TOP + AXIS_HEIGHT - 10}
                  textAnchor="middle"
                  fill="#424754"
                  fontSize={11}
                  fontFamily="Inter, sans-serif"
                  fontWeight={500}
                >
                  {year}
                </text>
              </g>
            );
          })}

          {/* ── Phase rows ──────────────────────────────────────────────── */}
          {phases.map((phase, index) => {
            const y =
              PADDING_TOP + AXIS_HEIGHT + index * (ROW_HEIGHT + ROW_GAP);
            const barX = yearToX(phase.start_year);
            const barWidth = yearToX(phase.end_year) - barX;
            const clampedWidth = Math.max(barWidth, 40);
            const barColor =
              WAVE_COLORS[phase.technology_wave as keyof typeof WAVE_COLORS] ??
              '#0058be';

            return (
              <g key={phase.name}>
                {/* Row background */}
                <rect
                  x={0}
                  y={y}
                  width={chartWidth}
                  height={ROW_HEIGHT}
                  fill={index % 2 === 0 ? '#f7f9fb' : 'transparent'}
                  rx={4}
                />

                {/* Phase label (left side) */}
                <text
                  x={12}
                  y={y + ROW_HEIGHT / 2 - 6}
                  fill="#191c1e"
                  fontSize={12}
                  fontFamily="Inter, sans-serif"
                  fontWeight={600}
                >
                  {phase.name}
                </text>
                <text
                  x={12}
                  y={y + ROW_HEIGHT / 2 + 10}
                  fill="#424754"
                  fontSize={10}
                  fontFamily="Inter, sans-serif"
                >
                  {phase.start_year} &ndash; {phase.end_year}
                </text>

                {/* Bar */}
                <rect
                  x={barX}
                  y={y + 6}
                  width={clampedWidth}
                  height={ROW_HEIGHT - 12}
                  fill={barColor}
                  rx={BAR_RADIUS}
                  opacity={0.9}
                />

                {/* Bar label: vehicles + budget inside bar */}
                {clampedWidth > 80 && (
                  <>
                    <text
                      x={barX + clampedWidth / 2}
                      y={y + ROW_HEIGHT / 2 - 4}
                      textAnchor="middle"
                      fill="white"
                      fontSize={11}
                      fontFamily="Inter, sans-serif"
                      fontWeight={600}
                    >
                      {phase.vehicles_to_convert} vehicules
                    </text>
                    <text
                      x={barX + clampedWidth / 2}
                      y={y + ROW_HEIGHT / 2 + 10}
                      textAnchor="middle"
                      fill="white"
                      fontSize={9}
                      fontFamily="Inter, sans-serif"
                      fontWeight={400}
                      opacity={0.85}
                    >
                      {fmtMAD(phase.budget_allocated_mad)}
                    </text>
                  </>
                )}

                {/* Fallback: short bar, show text to the right */}
                {clampedWidth <= 80 && (
                  <text
                    x={barX + clampedWidth + 6}
                    y={y + ROW_HEIGHT / 2 + 3}
                    fill="#424754"
                    fontSize={10}
                    fontFamily="Inter, sans-serif"
                    fontWeight={500}
                  >
                    {phase.vehicles_to_convert} veh. &middot;{' '}
                    {fmtMAD(phase.budget_allocated_mad)}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
