import { useEffect, useState, useMemo } from 'react';
import { AdvancedMarker, InfoWindow } from '@vis.gl/react-google-maps';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { MapView } from '@/components/maps/MapView';
import { getStopsAnalysis, type StopStat, type StopsAnalysis } from '@/api/transportOptimization';

/* ── AI suggestion types ─────────────────────────────────────────────────── */
type SuggestionType = 'REMOVE' | 'RELOCATE' | 'ADD' | 'MERGE';

interface StopSuggestion {
  id: string;
  type: SuggestionType;
  target_stop?: StopStat;
  partner_stop?: StopStat;
  suggested_lat?: number;
  suggested_lng?: number;
  reason: string;
  confidence: number;
  impact: string;
  priority: number;
}

function haversineMHaversineM(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371000;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

function buildSuggestions(stops: StopStat[]): StopSuggestion[] {
  const withCoords = stops.filter((s) => s.lat && s.lng);
  const suggestions: StopSuggestion[] = [];

  // Compute nearest neighbor distance for each stop
  const nearest: Map<string, { dist: number; stop: StopStat }> = new Map();
  for (const a of withCoords) {
    let bestDist = Infinity;
    let bestStop = a;
    for (const b of withCoords) {
      if (a.id === b.id) continue;
      const d = haversineMHaversineM(a.lat!, a.lng!, b.lat!, b.lng!);
      if (d < bestDist) { bestDist = d; bestStop = b; }
    }
    nearest.set(a.id, { dist: bestDist, stop: bestStop });
  }

  const usedIds = new Set<string>();

  // 1. MERGE: very close pairs (< 400m) with combined low utilization
  for (const s of withCoords) {
    if (usedIds.has(s.id)) continue;
    const nn = nearest.get(s.id);
    if (!nn || nn.dist > 400) continue;
    const partner = nn.stop;
    if (usedIds.has(partner.id)) continue;
    if (s.utilization_score + partner.utilization_score < 90) {
      const weaker = s.utilization_score <= partner.utilization_score ? s : partner;
      const stronger = weaker === s ? partner : s;
      usedIds.add(weaker.id);
      suggestions.push({
        id: `merge_${s.id}`,
        type: 'MERGE',
        target_stop: weaker,
        partner_stop: stronger,
        reason: `Arrêt à ${Math.round(nn.dist)}m de "${stronger.nom}" — ${Math.round(weaker.utilization_score)}% utilisation combinée`,
        confidence: Math.round(90 - nn.dist / 5),
        impact: `Réduction de 1 arrêt · Consolider ${weaker.usage_count} passage(s) vers "${stronger.nom}"`,
        priority: 2,
      });
    }
  }

  // 2. REMOVE: very underutilized AND poor walking score AND has a close neighbor
  for (const s of withCoords) {
    if (usedIds.has(s.id)) continue;
    const nn = nearest.get(s.id);
    if (!nn) continue;
    if (s.utilization_score < 28 && s.walking_score < 45 && nn.dist < 700) {
      usedIds.add(s.id);
      suggestions.push({
        id: `remove_${s.id}`,
        type: 'REMOVE',
        target_stop: s,
        reason: `Utilisation faible (${Math.round(s.utilization_score)}%) · Score marche ${Math.round(s.walking_score)}/100 · Arrêt "${nn.stop.nom}" à ${Math.round(nn.dist)}m`,
        confidence: Math.round(Math.max(50, 100 - s.utilization_score * 2)),
        impact: `Économie opérationnelle · ${s.usage_count} passage(s) à rediriger vers l'arrêt le plus proche`,
        priority: 3,
      });
    }
  }

  // 3. RELOCATE: poor walking score but decent utilization — can be improved
  for (const s of withCoords) {
    if (usedIds.has(s.id)) continue;
    if (s.walking_score < 42 && s.utilization_score > 35) {
      // Suggest moving to a better position: midpoint with nearest highly-scored neighbor
      const goodNeighbors = withCoords
        .filter((n) => n.id !== s.id && n.walking_score > 60)
        .sort((a, b) => haversineMHaversineM(s.lat!, s.lng!, a.lat!, a.lng!) - haversineMHaversineM(s.lat!, s.lng!, b.lat!, b.lng!));
      const ref = goodNeighbors[0];
      if (ref && haversineMHaversineM(s.lat!, s.lng!, ref.lat!, ref.lng!) < 2000) {
        const sugLat = (s.lat! + ref.lat!) / 2;
        const sugLng = (s.lng! + ref.lng!) / 2;
        suggestions.push({
          id: `relocate_${s.id}`,
          type: 'RELOCATE',
          target_stop: s,
          suggested_lat: sugLat,
          suggested_lng: sugLng,
          reason: `Score marche insuffisant (${Math.round(s.walking_score)}/100) malgré ${Math.round(s.utilization_score)}% d'utilisation`,
          confidence: 72,
          impact: `Amélioration accessibilité piétonne estimée +15-25 pts · Conserve les ${s.usage_count} utilisateurs`,
          priority: 4,
        });
      }
    }
  }

  // 4. ADD: cities where the largest inter-stop gap suggests a missing stop
  const byCity: Record<string, StopStat[]> = {};
  for (const s of withCoords) {
    const city = s.ville || 'Inconnu';
    (byCity[city] = byCity[city] ?? []).push(s);
  }
  for (const [city, cityStops] of Object.entries(byCity)) {
    if (cityStops.length < 3) continue;
    // Find the pair of stops with the largest gap
    let maxDist = 0;
    let pairA = cityStops[0];
    let pairB = cityStops[1];
    for (let i = 0; i < cityStops.length; i++) {
      for (let j = i + 1; j < cityStops.length; j++) {
        const d = haversineMHaversineM(cityStops[i].lat!, cityStops[i].lng!, cityStops[j].lat!, cityStops[j].lng!);
        if (d > maxDist) { maxDist = d; pairA = cityStops[i]; pairB = cityStops[j]; }
      }
    }
    if (maxDist > 900) {
      const midLat = (pairA.lat! + pairB.lat!) / 2;
      const midLng = (pairA.lng! + pairB.lng!) / 2;
      // Only add if no existing stop is within 450m of the midpoint
      const nearMid = withCoords.some((s) => haversineMHaversineM(midLat, midLng, s.lat!, s.lng!) < 450);
      if (!nearMid) {
        suggestions.push({
          id: `add_${city}`,
          type: 'ADD',
          suggested_lat: midLat,
          suggested_lng: midLng,
          reason: `Zone de ${city} sans arrêt dans un rayon de 450m · Écart de ${Math.round(maxDist)}m entre "${pairA.nom}" et "${pairB.nom}"`,
          confidence: 68,
          impact: `Améliore la couverture de ${city} · Réduction de marche estimée pour ~15-30 employés`,
          priority: 1,
        });
      }
    }
  }

  return suggestions.sort((a, b) => a.priority - b.priority || b.confidence - a.confidence);
}

const SUGGESTION_STYLE: Record<SuggestionType, { bg: string; text: string; border: string; icon: string; markerColor: string; label: string }> = {
  ADD:      { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', icon: 'add_location', markerColor: '#10b981', label: 'Ajouter' },
  REMOVE:   { bg: 'bg-red-50',     text: 'text-red-700',     border: 'border-red-200',     icon: 'wrong_location', markerColor: '#ef4444', label: 'Supprimer' },
  RELOCATE: { bg: 'bg-amber-50',   text: 'text-amber-700',   border: 'border-amber-200',   icon: 'edit_location', markerColor: '#f59e0b', label: 'Déplacer' },
  MERGE:    { bg: 'bg-violet-50',  text: 'text-violet-700',  border: 'border-violet-200',  icon: 'merge', markerColor: '#8b5cf6', label: 'Fusionner' },
};

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
  const [tab, setTab] = useState<'analyse' | 'suggestions'>('analyse');
  const [selectedSuggestion, setSelectedSuggestion] = useState<StopSuggestion | null>(null);
  const [suggFilterType, setSuggFilterType] = useState<SuggestionType | ''>('');

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

  const allSuggestions = useMemo(() => data ? buildSuggestions(data.stops) : [], [data]);
  const filteredSuggestions = useMemo(() => suggFilterType ? allSuggestions.filter((s) => s.type === suggFilterType) : allSuggestions, [allSuggestions, suggFilterType]);

  const suggMapCenter = useMemo((): [number, number] => {
    if (selectedSuggestion) {
      if (selectedSuggestion.suggested_lat && selectedSuggestion.suggested_lng) return [selectedSuggestion.suggested_lat, selectedSuggestion.suggested_lng];
      if (selectedSuggestion.target_stop?.lat && selectedSuggestion.target_stop?.lng) return [selectedSuggestion.target_stop.lat, selectedSuggestion.target_stop.lng];
    }
    return KHOURIBGA;
  }, [selectedSuggestion]);

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
      {/* Tab toggle */}
      <div className="flex items-center gap-2 bg-white border border-slate-100 rounded-xl p-1.5 self-start">
        <button onClick={() => setTab('analyse')}
          className={['flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors', tab === 'analyse' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'].join(' ')}>
          <span className="material-symbols-outlined text-base">analytics</span>Analyse des arrêts
        </button>
        <button onClick={() => setTab('suggestions')}
          className={['flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors relative', tab === 'suggestions' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'].join(' ')}>
          <span className="material-symbols-outlined text-base">auto_awesome</span>Suggestions IA
          {allSuggestions.length > 0 && tab !== 'suggestions' && (
            <span className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-amber-500 text-white text-[10px] font-black flex items-center justify-center">{allSuggestions.length}</span>
          )}
        </button>
      </div>

      {tab === 'suggestions' ? (
        /* ── SUGGESTIONS IA TAB ─────────────────────────────────────────── */
        <div className="flex flex-col gap-5">
          {/* Header banner */}
          <div className="bg-gradient-to-r from-violet-600 to-blue-600 rounded-xl p-5 text-white flex items-start gap-4">
            <span className="material-symbols-outlined text-4xl mt-1 opacity-90" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
            <div className="flex-1">
              <p className="text-lg font-black">Suggestions d'optimisation des arrêts</p>
              <p className="text-sm opacity-80 mt-1">Analyse algorithmique basée sur les scores d'utilisation, de marche, la proximité géographique et les gaps de couverture.</p>
              <div className="flex flex-wrap gap-3 mt-3">
                {(['ADD','REMOVE','RELOCATE','MERGE'] as SuggestionType[]).map((type) => {
                  const count = allSuggestions.filter((s) => s.type === type).length;
                  const st = SUGGESTION_STYLE[type];
                  return (
                    <button key={type} onClick={() => setSuggFilterType(suggFilterType === type ? '' : type)}
                      className={['flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold border-2 transition-all', suggFilterType === type ? 'bg-white text-slate-800 border-white' : 'border-white/40 text-white hover:border-white'].join(' ')}>
                      <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>{st.icon}</span>
                      {st.label} ({count})
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Left: suggestions list */}
            <div className="flex flex-col gap-3">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">{filteredSuggestions.length} suggestion(s)</p>
              <div className="flex flex-col gap-2 overflow-y-auto" style={{ maxHeight: 520 }}>
                {filteredSuggestions.length === 0 && (
                  <div className="text-center py-8 text-slate-400 text-sm">Aucune suggestion pour ce filtre</div>
                )}
                {filteredSuggestions.map((sugg) => {
                  const st = SUGGESTION_STYLE[sugg.type];
                  const isSelected = selectedSuggestion?.id === sugg.id;
                  return (
                    <button key={sugg.id} onClick={() => setSelectedSuggestion(isSelected ? null : sugg)}
                      className={['w-full text-left rounded-xl border p-3 transition-all', isSelected ? 'ring-2 ring-blue-500 ' + st.bg + ' ' + st.border : 'bg-white border-slate-100 hover:border-slate-200'].join(' ')}>
                      <div className="flex items-start gap-2">
                        <span className={['material-symbols-outlined text-lg mt-0.5', st.text].join(' ')} style={{ fontVariationSettings: "'FILL' 1" }}>{st.icon}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className={['text-[10px] font-black px-2 py-0.5 rounded-full', st.bg, st.text].join(' ')}>{st.label}</span>
                            <span className="text-xs font-bold text-slate-700 truncate">{sugg.target_stop?.nom ?? 'Nouveau point'}</span>
                          </div>
                          <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">{sugg.reason}</p>
                          <div className="flex items-center gap-2 mt-1.5">
                            <div className="flex-1 h-1 rounded-full bg-slate-100 overflow-hidden">
                              <div className="h-full rounded-full" style={{ width: `${sugg.confidence}%`, backgroundColor: sugg.confidence >= 75 ? '#10b981' : '#f59e0b' }} />
                            </div>
                            <span className="text-[10px] font-mono text-slate-400">{sugg.confidence}%</span>
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Center + Right: map */}
            <div className="lg:col-span-2 flex flex-col gap-3">
              {selectedSuggestion && (
                <div className={['rounded-xl border p-4 flex flex-col gap-2', SUGGESTION_STYLE[selectedSuggestion.type].bg, SUGGESTION_STYLE[selectedSuggestion.type].border].join(' ')}>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={['font-black text-sm', SUGGESTION_STYLE[selectedSuggestion.type].text].join(' ')}>
                          {SUGGESTION_STYLE[selectedSuggestion.type].label.toUpperCase()} — {selectedSuggestion.target_stop?.nom ?? 'Nouveau point'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-0.5">{selectedSuggestion.reason}</p>
                    </div>
                    <button onClick={() => setSelectedSuggestion(null)} className="text-slate-400 hover:text-slate-600">
                      <span className="material-symbols-outlined text-sm">close</span>
                    </button>
                  </div>
                  <div className="bg-white/70 rounded-lg px-3 py-2">
                    <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Impact estimé</p>
                    <p className="text-xs text-slate-700 mt-0.5">{selectedSuggestion.impact}</p>
                  </div>
                </div>
              )}
              <MapView center={suggMapCenter} zoom={selectedSuggestion ? 14 : 11} height="440px" className="rounded-xl">
                {/* Existing stops as grey dots */}
                {data.stops.filter((s) => s.lat && s.lng).map((s) => (
                  <AdvancedMarker key={s.id} position={{ lat: s.lat!, lng: s.lng! }}>
                    <div className="w-3 h-3 rounded-full bg-slate-300 border border-white shadow-sm opacity-60" />
                  </AdvancedMarker>
                ))}
                {/* Suggestion markers */}
                {filteredSuggestions.map((sugg) => {
                  const lat = sugg.suggested_lat ?? sugg.target_stop?.lat;
                  const lng = sugg.suggested_lng ?? sugg.target_stop?.lng;
                  if (!lat || !lng) return null;
                  const st = SUGGESTION_STYLE[sugg.type];
                  const isSelected = selectedSuggestion?.id === sugg.id;
                  return (
                    <AdvancedMarker key={sugg.id} position={{ lat, lng }} onClick={() => setSelectedSuggestion(isSelected ? null : sugg)}>
                      <div className={['flex flex-col items-center cursor-pointer transition-transform', isSelected ? 'scale-150' : 'hover:scale-125'].join(' ')}>
                        <div className="w-8 h-8 rounded-full flex items-center justify-center shadow-lg border-2 border-white"
                          style={{ backgroundColor: st.markerColor }}>
                          <span className="material-symbols-outlined text-white text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>{st.icon}</span>
                        </div>
                        {isSelected && <div className="w-0.5 h-3 mt-0.5" style={{ backgroundColor: st.markerColor }} />}
                      </div>
                    </AdvancedMarker>
                  );
                })}
              </MapView>
              {/* Legend */}
              <div className="flex flex-wrap gap-3 justify-center">
                {(['ADD','REMOVE','RELOCATE','MERGE'] as SuggestionType[]).map((type) => {
                  const st = SUGGESTION_STYLE[type];
                  const count = allSuggestions.filter((s) => s.type === type).length;
                  return (
                    <span key={type} className="flex items-center gap-1.5 text-xs text-slate-500">
                      <span className="w-3 h-3 rounded-full" style={{ backgroundColor: st.markerColor }} />
                      {st.label} ({count})
                    </span>
                  );
                })}
                <span className="flex items-center gap-1.5 text-xs text-slate-400">
                  <span className="w-3 h-3 rounded-full bg-slate-300" />Arrêt existant
                </span>
              </div>
            </div>
          </div>
        </div>
      ) : (
      <>
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
                  formatter={(v, name) => [v, (name as string) === 'count' ? 'Total' : 'Actifs']}
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
      </>
      )}
    </div>
  );
}
