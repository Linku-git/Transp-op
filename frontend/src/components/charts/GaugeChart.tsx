import { useMemo } from 'react';

interface GaugeChartProps {
  value: number; // 0-100 percentage
  label?: string;
  size?: number; // diameter in px, default 120
  color?: string; // arc color, default '#006b5c'
}

export function GaugeChart({
  value,
  label,
  size = 120,
  color = '#006b5c',
}: GaugeChartProps) {
  const clamped = Math.max(0, Math.min(100, value));

  const geometry = useMemo(() => {
    const strokeWidth = 10;
    const radius = size / 2 - strokeWidth;
    const cx = size / 2;
    const cy = size / 2;

    // Semicircle arc length
    const circumference = Math.PI * radius;
    const dashoffset = circumference * (1 - clamped / 100);

    // SVG arc endpoints for the semicircle (180 degrees, opening upward)
    // Start point: left end of semicircle
    const startX = cx - radius;
    const startY = cy;
    // End point: right end of semicircle
    const endX = cx + radius;
    const endY = cy;

    // Arc path: from left to right following upper semicircle
    const arcPath = `M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`;

    return {
      strokeWidth,
      radius,
      cx,
      cy,
      circumference,
      dashoffset,
      arcPath,
    };
  }, [size, clamped]);

  return (
    <div className="flex flex-col items-center">
      <svg
        width={size}
        height={size / 2 + 8}
        viewBox={`0 0 ${size} ${size / 2 + 8}`}
        role="img"
        aria-label={`${clamped}%${label ? ` ${label}` : ''}`}
      >
        {/* Background arc */}
        <path
          d={geometry.arcPath}
          fill="none"
          stroke="#dde8f0"
          strokeWidth={geometry.strokeWidth}
          strokeLinecap="round"
        />
        {/* Foreground arc (value) */}
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
        {/* Center text */}
        <text
          x={geometry.cx}
          y={geometry.cy - 4}
          textAnchor="middle"
          dominantBaseline="auto"
          className="font-display"
          fill="#111d23"
          fontSize={size * 0.18}
          fontWeight={700}
        >
          {clamped.toFixed(0)}%
        </text>
      </svg>
      {label && (
        <span className="font-sans text-xs text-on-surface-variant mt-1">
          {label}
        </span>
      )}
    </div>
  );
}
