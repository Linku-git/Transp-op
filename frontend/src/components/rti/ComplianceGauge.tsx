export function ComplianceGauge({ value, label = 'Conformité RTI' }: { value: number; label?: string }) {
  const color = value >= 95 ? 'text-green-600' : value >= 85 ? 'text-amber-500' : 'text-error';
  const bgColor = value >= 95 ? 'stroke-green-100' : value >= 85 ? 'stroke-amber-100' : 'stroke-red-100';
  const fgColor = value >= 95 ? 'stroke-green-500' : value >= 85 ? 'stroke-amber-500' : 'stroke-red-500';
  const circumference = 2 * Math.PI * 60;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 flex flex-col items-center">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">{label}</p>
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 130 130">
          <circle cx="65" cy="65" r="60" fill="none" strokeWidth="10" className={bgColor} />
          <circle
            cx="65" cy="65" r="60" fill="none" strokeWidth="10"
            className={fgColor}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold ${color}`}>{value.toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
}
