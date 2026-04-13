import { useState, useEffect, useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { useDriverStore } from '@/stores/driverStore';
import type { DriverRiskProfile } from '@/api/driver';

/* ── Demo data ─────────────────────────────────────────────────────────── */

function generateScoreHistory(): { date: string; score: number }[] {
  const history: { date: string; score: number }[] = [];
  const base = new Date('2026-03-14');
  let score = 72;
  for (let i = 0; i < 30; i++) {
    const d = new Date(base);
    d.setDate(d.getDate() + i);
    // Trend upward with some noise
    score = Math.min(100, Math.max(0, score + (Math.random() * 4 - 1.5)));
    history.push({
      date: d.toISOString().slice(0, 10),
      score: Math.round(score),
    });
  }
  return history;
}

const DEMO_RISK: DriverRiskProfile = {
  driver_id: 'drv-001',
  risk_score: 78,
  risk_category: 'medium',
  infractions: {
    speed: 12,
    acceleration: 8,
    braking: 15,
    geofence: 2,
    driving_time: 5,
  },
  score_history: generateScoreHistory(),
  tips: [
    'Reduisez votre vitesse dans les zones urbaines pour ameliorer votre score de freinage',
    'Anticipez les arrets pour eviter les freinages brusques',
    'Respectez les temps de pause reglementaires entre les trajets',
    'Maintenez une acceleration progressive au demarrage',
  ],
};

/* ── Risk category config ──────────────────────────────────────────────── */

const RISK_CATEGORIES: Record<
  DriverRiskProfile['risk_category'],
  { label: string; color: string; bgClass: string; textClass: string }
> = {
  low: {
    label: 'Faible',
    color: '#16a34a',
    bgClass: 'bg-green-50',
    textClass: 'text-green-700',
  },
  medium: {
    label: 'Moyen',
    color: '#d97706',
    bgClass: 'bg-amber-50',
    textClass: 'text-amber-700',
  },
  high: {
    label: 'Eleve',
    color: '#ea580c',
    bgClass: 'bg-orange-50',
    textClass: 'text-orange-700',
  },
  critical: {
    label: 'Critique',
    color: '#dc2626',
    bgClass: 'bg-error-container/30',
    textClass: 'text-error',
  },
};

/* ── Infraction labels ─────────────────────────────────────────────────── */

const INFRACTION_LABELS: Record<string, { label: string; icon: string }> = {
  speed: { label: 'Vitesse', icon: 'speed' },
  acceleration: { label: 'Acceleration', icon: 'trending_up' },
  braking: { label: 'Freinage', icon: 'trending_down' },
  geofence: { label: 'Geofence', icon: 'location_off' },
  driving_time: { label: 'Temps conduite', icon: 'timer' },
};

/* ── Component ─────────────────────────────────────────────────────────── */

export function DriverRiskPage() {
  const { setRiskProfile } = useDriverStore();
  const [risk, setLocalRisk] = useState<DriverRiskProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLocalRisk(DEMO_RISK);
      setRiskProfile(DEMO_RISK);
      setLoading(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [setRiskProfile]);

  const maxInfraction = useMemo(() => {
    if (!risk) return 0;
    return Math.max(...Object.values(risk.infractions));
  }, [risk]);

  const categoryConfig = risk
    ? RISK_CATEGORIES[risk.risk_category]
    : RISK_CATEGORIES.low;

  // Gauge calculations
  const scoreAngle = risk ? (risk.risk_score / 100) * 180 : 0;
  const gaugeRadius = 80;
  const gaugeStroke = 12;

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-on-surface-variant text-sm">
        <span className="material-symbols-outlined animate-spin mr-2">
          progress_activity
        </span>
        Chargement du score...
      </div>
    );
  }

  if (!risk) {
    return (
      <div
        className="flex-1 flex flex-col items-center justify-center gap-3"
        data-testid="risk-empty"
      >
        <span className="material-symbols-outlined text-5xl text-on-surface-variant/40">
          shield
        </span>
        <p className="text-sm text-on-surface-variant">
          Aucune donnee de risque disponible
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="driver-risk-page">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-on-surface">Mon Score</h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Score de conduite et recommandations d&apos;amelioration
        </p>
      </div>

      {/* Score gauge + category */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gauge card */}
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 flex flex-col items-center">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
            Score de conduite
          </p>

          {/* SVG Gauge */}
          <div className="relative" data-testid="risk-gauge">
            <svg
              width={gaugeRadius * 2 + gaugeStroke * 2}
              height={gaugeRadius + gaugeStroke * 2 + 10}
              viewBox={`0 0 ${gaugeRadius * 2 + gaugeStroke * 2} ${gaugeRadius + gaugeStroke * 2 + 10}`}
            >
              {/* Background arc */}
              <path
                d={`M ${gaugeStroke} ${gaugeRadius + gaugeStroke} A ${gaugeRadius} ${gaugeRadius} 0 0 1 ${gaugeRadius * 2 + gaugeStroke} ${gaugeRadius + gaugeStroke}`}
                fill="none"
                stroke="#e6e8ea"
                strokeWidth={gaugeStroke}
                strokeLinecap="round"
              />
              {/* Score arc */}
              <path
                d={`M ${gaugeStroke} ${gaugeRadius + gaugeStroke} A ${gaugeRadius} ${gaugeRadius} 0 0 1 ${gaugeStroke + gaugeRadius - gaugeRadius * Math.cos((scoreAngle * Math.PI) / 180)} ${gaugeRadius + gaugeStroke - gaugeRadius * Math.sin((scoreAngle * Math.PI) / 180)}`}
                fill="none"
                stroke={categoryConfig.color}
                strokeWidth={gaugeStroke}
                strokeLinecap="round"
              />
            </svg>
            {/* Score number centered */}
            <div className="absolute inset-0 flex items-end justify-center pb-2">
              <span
                className="text-4xl font-bold"
                style={{ color: categoryConfig.color }}
                data-testid="risk-score-value"
              >
                {risk.risk_score}
              </span>
            </div>
          </div>

          <span
            className={[
              'inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold mt-3',
              categoryConfig.bgClass,
              categoryConfig.textClass,
            ].join(' ')}
            data-testid="risk-category-badge"
          >
            Risque {categoryConfig.label}
          </span>
          <p className="text-xs text-on-surface-variant mt-2 text-center">
            Score sur 100 — Plus le score est eleve, meilleure est la conduite
          </p>
        </div>

        {/* Score history chart */}
        <div className="lg:col-span-2 bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
            Evolution du score (30 jours)
          </p>
          <div className="h-56" data-testid="score-history-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={risk.score_history}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#c2c6d6"
                  strokeOpacity={0.3}
                />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: '#424754' }}
                  tickFormatter={(v: string) => v.slice(5)}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 10, fill: '#424754' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #c2c6d6',
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelFormatter={(l: string) =>
                    new Date(l).toLocaleDateString('fr-FR')
                  }
                  formatter={(v: number) => [`${v}/100`, 'Score']}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke={categoryConfig.color}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Infraction breakdown */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          Repartition des infractions
        </p>
        <div className="space-y-4">
          {Object.entries(risk.infractions).map(([key, count]) => {
            const infConfig = INFRACTION_LABELS[key];
            if (!infConfig) return null;
            const pct = maxInfraction > 0 ? (count / maxInfraction) * 100 : 0;
            return (
              <div
                key={key}
                className="flex items-center gap-4"
                data-testid={`infraction-${key}`}
              >
                <div className="flex items-center gap-2 w-40 shrink-0">
                  <span className="material-symbols-outlined text-on-surface-variant text-lg">
                    {infConfig.icon}
                  </span>
                  <span className="text-sm text-on-surface font-medium">
                    {infConfig.label}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="h-3 rounded-full bg-surface-container-high overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary to-primary-container transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm font-bold text-on-surface w-10 text-right">
                  {count}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          Conseils d&apos;amelioration
        </p>
        <div className="space-y-3" data-testid="risk-tips">
          {risk.tips.map((tip, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 bg-primary/5 rounded-lg p-4"
            >
              <span className="material-symbols-outlined text-primary text-lg shrink-0 mt-0.5">
                lightbulb
              </span>
              <p className="text-sm text-on-surface">{tip}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
