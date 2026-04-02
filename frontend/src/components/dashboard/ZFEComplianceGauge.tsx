import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

interface ZFEComplianceGaugeProps {
  compliantCount: number;
  totalCount: number;
  compliancePct: number;
}

function getGaugeColor(pct: number): string {
  if (pct >= 80) return '#16a34a';
  if (pct >= 50) return '#d97706';
  return '#ba1a1a';
}

export function ZFEComplianceGauge({
  compliantCount,
  totalCount,
  compliancePct,
}: ZFEComplianceGaugeProps) {
  const { t } = useTranslation();
  const clamped = Math.max(0, Math.min(100, compliancePct));
  const color = getGaugeColor(clamped);
  const size = 160;

  const geometry = useMemo(() => {
    const strokeWidth = 12;
    const radius = size / 2 - strokeWidth;
    const cx = size / 2;
    const cy = size / 2;
    const circumference = Math.PI * radius;
    const dashoffset = circumference * (1 - clamped / 100);
    const startX = cx - radius;
    const startY = cy;
    const endX = cx + radius;
    const endY = cy;
    const arcPath = `M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`;

    return { strokeWidth, cx, cy, circumference, dashoffset, arcPath };
  }, [clamped]);

  return (
    <div className="flex flex-col items-center" data-testid="zfe-gauge">
      <svg
        width={size}
        height={size / 2 + 16}
        viewBox={`0 0 ${size} ${size / 2 + 16}`}
        role="img"
        aria-label={`${clamped.toFixed(0)}% ZFE compliance`}
      >
        {/* Background arc */}
        <path
          d={geometry.arcPath}
          fill="none"
          stroke="#dde8f0"
          strokeWidth={geometry.strokeWidth}
          strokeLinecap="round"
        />
        {/* Foreground arc */}
        <path
          d={geometry.arcPath}
          fill="none"
          stroke={color}
          strokeWidth={geometry.strokeWidth}
          strokeLinecap="round"
          strokeDasharray={geometry.circumference}
          strokeDashoffset={geometry.dashoffset}
          className="transition-all duration-500 ease-out"
        />
        {/* Percentage text */}
        <text
          x={geometry.cx}
          y={geometry.cy - 8}
          textAnchor="middle"
          dominantBaseline="auto"
          className="font-sans"
          fill={color}
          fontSize={size * 0.22}
          fontWeight={900}
          data-testid="zfe-pct"
        >
          {clamped.toFixed(0)}%
        </text>
      </svg>
      <span className="font-sans text-sm text-on-surface-variant -mt-1">
        {compliantCount}/{totalCount} {t('rse.vehicles', 'vehicules')}
      </span>
    </div>
  );
}
