import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface Props {
  distribution: { low: number; medium: number; high: number; critical: number };
}

const COLORS = { low: '#1B7D3A', medium: '#E67E22', high: '#E74C3C', critical: '#8B0000' };
const LABELS = { low: 'Faible', medium: 'Moyen', high: 'Élevé', critical: 'Critique' };

export function ScoreDistributionChart({ distribution }: Props) {
  const data = Object.entries(distribution).map(([key, value]) => ({
    name: LABELS[key as keyof typeof LABELS],
    count: value,
    key,
  }));

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        Distribution des scores de sécurité
      </p>
      {data.every((d) => d.count === 0) ? (
        <p className="text-sm text-on-surface-variant text-center py-8">Aucune donnée</p>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(215,228,236,0.2)" />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#72767F' }} />
            <YAxis tick={{ fontSize: 10, fill: '#72767F' }} />
            <Tooltip />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {data.map((entry) => (
                <Cell key={entry.key} fill={COLORS[entry.key as keyof typeof COLORS]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
