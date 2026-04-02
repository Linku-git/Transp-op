import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

interface CostPerTripGaugeProps {
  actual: number;
  target: number;
}

export function CostPerTripGauge({ actual, target }: CostPerTripGaugeProps) {
  const { t } = useTranslation();

  const delta = actual - target;
  const ratio = target > 0 ? actual / target : 1;

  const { color, bgColor, label } = useMemo(() => {
    if (ratio <= 0.9) {
      return { color: '#16a34a', bgColor: 'bg-green-50', label: t('financial.under_target', 'Sous objectif') };
    }
    if (ratio <= 1.1) {
      return { color: '#d97706', bgColor: 'bg-amber-50', label: t('financial.near_target', 'Proche objectif') };
    }
    return { color: '#dc2626', bgColor: 'bg-red-50', label: t('financial.over_target', 'Au-dessus objectif') };
  }, [ratio, t]);

  // SVG gauge arc
  const size = 160;
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const cx = size / 2;
  const cy = size / 2;

  // Semicircle from left to right
  const startX = cx - radius;
  const startY = cy;
  const endX = cx + radius;
  const endY = cy;
  const arcPath = `M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`;
  const circumference = Math.PI * radius;

  // Clamp the fill between 0 and 100%
  const fillPercent = Math.max(0, Math.min(100, (ratio / 1.5) * 100));
  const dashoffset = circumference * (1 - fillPercent / 100);

  return (
    <div data-testid="cost-per-trip-gauge" className={`${bgColor} rounded-xl p-6 flex flex-col items-center`}>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
        {t('financial.cost_per_trip', 'Cout par trajet')}
      </p>

      <svg
        width={size}
        height={size / 2 + 16}
        viewBox={`0 0 ${size} ${size / 2 + 16}`}
        role="img"
        aria-label={`${actual.toFixed(1)} MAD`}
      >
        {/* Background arc */}
        <path
          d={arcPath}
          fill="none"
          stroke="#dde8f0"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Value arc */}
        <path
          d={arcPath}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashoffset}
          className="transition-all duration-500 ease-out"
        />
        {/* Center value */}
        <text
          x={cx}
          y={cy - 8}
          textAnchor="middle"
          dominantBaseline="auto"
          fill={color}
          fontSize={28}
          fontWeight={900}
          className="font-sans"
        >
          {actual.toFixed(1)}
        </text>
        <text
          x={cx}
          y={cy + 8}
          textAnchor="middle"
          dominantBaseline="hanging"
          fill="#424754"
          fontSize={11}
          className="font-sans"
        >
          MAD
        </text>
      </svg>

      <div className="mt-2 text-center space-y-1">
        <p className="text-xs font-bold" style={{ color }}>
          {label}
        </p>
        <div className="flex items-center gap-3 text-xs text-on-surface-variant">
          <span>
            {t('financial.target_label', 'Objectif')}: {target.toFixed(1)} MAD
          </span>
          <span className="font-bold" style={{ color }}>
            {delta >= 0 ? '+' : ''}{delta.toFixed(1)}
          </span>
        </div>
      </div>
    </div>
  );
}
