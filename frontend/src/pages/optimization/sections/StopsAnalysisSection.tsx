import { useEffect, useState, useMemo } from 'react';
import { AdvancedMarker, InfoWindow } from '@vis.gl/react-google-maps';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { MapView } from '@/components/maps/MapView';
import { getStopsAnalysis, type StopStat, type StopsAnalysis } from '@/api/transportOptimization';

/* ── Colour helpers ──────────────────────────────────────────────────────── */
const CITY_COLORS = ['#3b82f6','#f59e0b','#10b981','#8b5cf6','#f97316','#06b6d4','#ec4899'];

function scoreColor(score: number): string {
  if (score >= 80) return '#10b981';
  if (score >= 60) return '#f59e0b';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}
function scoreLabel(score: number): string {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Bon';
  if (score >= 40) return 'Moyen';
  return 'Faible';
}

function ScoreBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="flex items-center gap-2 flex-1">
      <div className="flex-1 h-1.5 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
      <span className="text-[11px] font-mono w-7 text-right" style={{ color }}>{Math.round(value)}</span>
    </div>
  );
}

function ScoreBadge({ value }: { value: number }) {
  const color = scoreColor(value);
  const label = scoreLabel(value);
  return (
    <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold" style={{ backgroundColor: color + '20', color }}>
      {label}
    </span>
  );
}

function StatCard({ icon, label, value, sub }: { icon: string; label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-100 px-4 py-3 flex items-center gap-3">
      <span className="material-symbols-outlined text-2xl text-blue-500" style={{ fontVariationSettings: "'FILL' 1" }}>{icon}</span>
      <div>
        <p className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">{label}</p>
        <p className="text-xl font-black text-slate-800">{value}</p>
        {sub && <p className="text-[10px] text-slate-400">{sub}</p>}
      </div>
    </div>
  );
}

/* ── KHOURIBGA area center ───────────────────────────────────────────────── */
const KHOURIBGA: [number, number] = [32.886, -6.907];

/* ── Main Component ──────────────────────────────────────────────────────── */
export function StopsAnalysisSection() {
  const [data, setData] = useState<StopsAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStop, setSelectedStop] = useState<StopStat | null>(null);
  const [filterCity, setFilterCity] = useState('');
  const [sortBy, setSortBy] = useState<'walking_score' | 'utilization_score' | 'nom'>('walking_score');
  const [openMarkerId, setOpenMarkerId] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getStopsAnalysis()
      .then(setData)
      .catch((e) => setError(e.message || 'Erreur'))
      .finally(() => setLoading(false));
  }, []);

  const filteredStops = useMemo(() => {
    if (!data) return [];
    let stops = data.stops;
    if (filterCity) stops = stops.filter((s) => s.ville === filterCity);
    return [...stops].sort((a, b) => {
      if (sortBy === 'nom') return (a.nom || '').localeCompare(b.nom || '');
      return b[sortBy] - a[sortBy];
    });
  }, [data, filterCity, sortBy]);

  const cityChartData = useMemo(() => {
    if (!data) return [];
    return data.cities.map((c, i) => ({ name: c.name, count: c.count, active: c.active, color: CITY_COLORS[i % CITY_COLORS.length] }));
  }, [data]);

  const mapCenter = useMemo(() => {
    if (!data || !filterCity) return KHOURIBGA;
    const city = data.stops.find((s) => s.ville === filterCity && s.lat && s.lng);
    if (city && city.lat && city.lng) return [city.lat, city.lng] as [number, number];
    return KHOURIBGA;
  }, [data, filterCity]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        <span className="material-symbols-outlined text-4xl animate-spin mr-3">progress_activity</span>
        Chargement de l'analyse des arrêts…
      </div>
    );
  }
  if (error || !data) {
    return <div className="text-red-500 p-4">Erreur: {error}</div>;
  }

  const avgWalking = data.stops.length ? data.stops.reduce((s, x) => s + x.walking_score, 0) / data.stops.length : 0;
  const avgUtil = data.stops.length ? data.stops.reduce((s, x) => s + x.utilization_score, 0) / data.stops.length : 0;

  return (
    <div className="flex flex-col gap-5">
      {/* KPI strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard icon="location_on" label="Total arrêts" value={data.total_stops} sub={`${data.active_stops} actifs`} />
        <StatCard icon="location_city" label="Villes couvertes" value={data.cities.length} sub={`${Math.round(data.coverage_pct)}% routes couvertes`} />
        <StatCard icon="directions_walk" label="Score marche moy." value={`${Math.round(avgWalking)}/100`} sub={scoreLabel(avgWalking)} />
        <StatCard icon="analytics" label="Utilisation moy." value={`${Math.round(avgUtil)}/100`} sub={`${Math.round(data.avg_usage)} réf. config.`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left: map */}
        <div className="lg:col-span-2 flex flex-col gap-3">
          {/* Filters */}
          <div className="flex flex-wrap items-center gap-3 bg-white border border-slate-100 rounded-xl px-4 py-2.5">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Filtres</span>
            <select
              value={filterCity}
              onChange={(e) => setFilterCity(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 appearance-none"
            >
              <option value="">Toutes les villes</option>
              {data.cities.map((c) => <option key={c.name} value={c.name}>{c.name} ({c.count})</option>)}
            </select>
            <div className="ml-auto flex items-center gap-2">
              <span className="flex items-center gap-1 text-xs text-slate-400">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500" /> Excellent (≥80)
              </span>
              <span className="flex items-center gap-1 text-xs text-slate-400">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-amber-500" /> Bon (60-80)
              </span>
              <span className="flex items-center gap-1 text-xs text-slate-400">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-red-500" /> Faible (&lt;60)
              </span>
            </div>
          </div>

          {/* Map */}
          <MapView center={mapCenter} zoom={filterCity ? 14 : 11} height="420px" className="rounded-xl">
            {filteredStops.map((stop) => {
              if (!stop.lat || !stop.lng) return null;
              const color = scoreColor(stop.walking_score);
              return (
                <AdvancedMarker
                  key={stop.id}
                  position={{ lat: stop.lat, lng: stop.lng }}
                  onClick={() => setOpenMarkerId(openMarkerId === stop.id ? null : stop.id)}
                >
                  <div
                    className="flex flex-col items-center cursor-pointer group"
                    onClick={() => setSelectedStop(stop)}
                  >
                    <div
                      className="w-7 h-7 rounded-full border-2 border-white shadow-md flex items-center justify-center text-white text-[9px] font-black transition-transform group-hover:scale-125"
                      style={{ backgroundColor: color }}
                    >
                      {stop.code?.replace(/[A-Z]+/, '').slice(0, 2) || '?'}
                    </div>
                  </div>
                  {openMarkerId === stop.id && (
                    <InfoWindow position={{ lat: stop.lat, lng: stop.lng }} onCloseClick={() => setOpenMarkerId(null)}>
                      <div className="text-xs min-w-[160px]">
                        <p className="font-bold text-sm mb-1">{stop.nom}</p>
                        <p className="text-slate-500">{stop.code} · {stop.ville}</p>
                        {stop.prestataire && <p className="text-slate-500">Préstataire: {stop.prestataire}</p>}
                        <div className="mt-2 flex flex-col gap-1">
                          <div className="flex justify-between">
                            <span className="text-slate-400">Score marche</span>
                            <span className="font-bold" style={{ color }}>{Math.round(stop.walking_score)}/100</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Utilisation</span>
                            <span className="font-bold">{Math.round(stop.utilization_score)}/100</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Rayon couv.</span>
                            <span className="font-bold">{stop.coverage_radius_m}m</span>
                          </div>
                        </div>
                      </div>
                    </InfoWindow>
                  )}
                </AdvancedMarker>
              );
            })}
          </MapView>
        </div>

        {/* Right panel */}
        <div className="flex flex-col gap-4">
          {/* City distribution chart */}
          <div className="bg-white rounded-xl border border-slate-100 p-4">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Distribution par ville</p>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={cityChartData} margin={{ left: -20, right: 0, top: 4, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ fontSize: 11, borderRadius: 8 }}
                  formatter={(v: number, name: string) => [v, name === 'count' ? 'Total' : 'Actifs']}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {cityChartData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Stop selected detail */}
          {selectedStop && (
            <div className="bg-slate-900 text-white rounded-xl p-4 flex flex-col gap-3">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-bold text-base">{selectedStop.nom}</p>
                  <p className="text-slate-400 text-xs">{selectedStop.code} · {selectedStop.ville}</p>
                </div>
                <button onClick={() => setSelectedStop(null)} className="text-slate-500 hover:text-white">
                  <span className="material-symbols-outlined text-sm">close</span>
                </button>
              </div>
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Score marche</span>
                  <ScoreBadge value={selectedStop.walking_score} />
                </div>
                <ScoreBar value={selectedStop.walking_score} color={scoreColor(selectedStop.walking_score)} />
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-slate-400">Utilisation</span>
                  <ScoreBadge value={selectedStop.utilization_score} />
                </div>
                <ScoreBar value={selectedStop.utilization_score} color={scoreColor(selectedStop.utilization_score)} />
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs mt-1">
                <div className="bg-slate-800 rounded-lg p-2">
                  <p className="text-slate-400">Rayon couverture</p>
                  <p className="font-bold text-white">{selectedStop.coverage_radius_m} m</p>
                </div>
                <div className="bg-slate-800 rounded-lg p-2">
                  <p className="text-slate-400">Statut</p>
                  <p className={['font-bold', selectedStop.is_active ? 'text-emerald-400' : 'text-red-400'].join(' ')}>
                    {selectedStop.is_active ? 'Actif' : 'Inactif'}
                  </p>
                </div>
                <div className="bg-slate-800 rounded-lg p-2 col-span-2">
                  <p className="text-slate-400">Préstataire</p>
                  <p className="font-bold text-white">{selectedStop.prestataire || '—'}</p>
                </div>
              </div>
              {selectedStop.lat && selectedStop.lng && (
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${selectedStop.lat},${selectedStop.lng}`}
                  target="_blank" rel="noreferrer"
                  className="flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300 mt-1"
                >
                  <span className="material-symbols-outlined text-sm">open_in_new</span>
                  Voir sur Google Maps
                </a>
              )}
            </div>
          )}

          {/* Stop list */}
          <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Arrêts ({filteredStops.length})</p>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-slate-600 appearance-none"
              >
                <option value="walking_score">Par marche</option>
                <option value="utilization_score">Par utilisation</option>
                <option value="nom">Par nom</option>
              </select>
            </div>
            <div className="overflow-y-auto" style={{ maxHeight: 280 }}>
              {filteredStops.map((stop) => (
                <button
                  key={stop.id}
                  onClick={() => setSelectedStop(selectedStop?.id === stop.id ? null : stop)}
                  className={[
                    'w-full text-left px-4 py-2.5 border-b border-slate-50 hover:bg-blue-50/50 transition-colors flex items-center gap-3',
                    selectedStop?.id === stop.id ? 'bg-blue-50' : '',
                  ].join(' ')}
                >
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: scoreColor(stop.walking_score) }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-slate-700 truncate">{stop.nom}</p>
                    <p className="text-[10px] text-slate-400 truncate">{stop.code} · {stop.ville}</p>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 shrink-0">{Math.round(stop.walking_score)}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
