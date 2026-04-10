import { useState, useCallback, useMemo } from 'react';
import { computeSupernetworkEquilibrium } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  SupernetworkLink,
  SupernetworkDemand,
  SupernetworkResponse,
  LinkFlow,
} from '@/types/sotreg';

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

function fmtMAD(value: number): string {
  return `${madFmt.format(value)} MAD`;
}

/* ── SVG layout engine ────────────────────────────────────────────────────── */

interface NodePosition {
  id: number;
  x: number;
  y: number;
}

function computeNodePositions(
  links: Array<{ from_node: number; to_node: number }>,
  demands: Array<{ origin: number; destination: number }>,
): NodePosition[] {
  const nodeSet = new Set<number>();
  for (const l of links) {
    nodeSet.add(l.from_node);
    nodeSet.add(l.to_node);
  }
  for (const d of demands) {
    nodeSet.add(d.origin);
    nodeSet.add(d.destination);
  }

  const nodes = Array.from(nodeSet).sort((a, b) => a - b);
  const count = nodes.length;
  if (count === 0) return [];

  /* Place nodes in a circle layout */
  const cx = 300;
  const cy = 200;
  const radius = Math.min(cx, cy) - 50;

  return nodes.map((id, i) => {
    const angle = (2 * Math.PI * i) / count - Math.PI / 2;
    return {
      id,
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  });
}

function getNodePos(
  positions: NodePosition[],
  nodeId: number,
): { x: number; y: number } {
  const found = positions.find((p) => p.id === nodeId);
  return found ?? { x: 0, y: 0 };
}

/* ── Arrow marker ─────────────────────────────────────────────────────────── */

function ArrowDefs() {
  return (
    <defs>
      <marker
        id="flow-arrow"
        viewBox="0 0 10 7"
        refX="9"
        refY="3.5"
        markerWidth="8"
        markerHeight="6"
        orient="auto-start-reverse"
      >
        <polygon points="0 0, 10 3.5, 0 7" fill="#0058be" />
      </marker>
      <marker
        id="flow-arrow-light"
        viewBox="0 0 10 7"
        refX="9"
        refY="3.5"
        markerWidth="8"
        markerHeight="6"
        orient="auto-start-reverse"
      >
        <polygon points="0 0, 10 3.5, 0 7" fill="#495e8a" />
      </marker>
    </defs>
  );
}

/* ── Edge SVG component ───────────────────────────────────────────────────── */

function FlowEdge({
  from,
  to,
  flow,
  cost,
  maxFlow,
}: {
  from: { x: number; y: number };
  to: { x: number; y: number };
  flow: number;
  cost: number;
  maxFlow: number;
}) {
  /* Thickness proportional to flow, min 1.5, max 8 */
  const thickness = maxFlow > 0
    ? 1.5 + (flow / maxFlow) * 6.5
    : 2;

  /* Offset the line so it doesn't go through the node circle (r=22) */
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist === 0) return null;

  const nodeRadius = 22;
  const ux = dx / dist;
  const uy = dy / dist;
  const x1 = from.x + ux * nodeRadius;
  const y1 = from.y + uy * nodeRadius;
  const x2 = to.x - ux * (nodeRadius + 10);
  const y2 = to.y - uy * (nodeRadius + 10);

  /* Label position: midpoint with slight perpendicular offset */
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const perpX = -uy * 14;
  const perpY = ux * 14;

  const hasFlow = flow > 0;

  return (
    <g>
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={hasFlow ? '#0058be' : '#c2c6d6'}
        strokeWidth={thickness}
        strokeOpacity={hasFlow ? 0.7 : 0.3}
        markerEnd={hasFlow ? 'url(#flow-arrow)' : 'url(#flow-arrow-light)'}
      />
      {/* Flow / cost label */}
      <text
        x={mx + perpX}
        y={my + perpY}
        textAnchor="middle"
        dominantBaseline="central"
        fontFamily="Inter, sans-serif"
        fontSize={10}
        fill="#424754"
      >
        <tspan fontWeight={600}>{madFmt.format(flow)}</tspan>
        <tspan dx={4} fill="#64748b">
          ({madFmt.format(cost)})
        </tspan>
      </text>
    </g>
  );
}

/* ── Node SVG component ───────────────────────────────────────────────────── */

function NetworkNode({ id, x, y }: { id: number; x: number; y: number }) {
  return (
    <g>
      <circle
        cx={x}
        cy={y}
        r={22}
        fill="#f7f9fb"
        stroke="#0058be"
        strokeWidth={2}
      />
      <text
        x={x}
        y={y}
        textAnchor="middle"
        dominantBaseline="central"
        fontFamily="Inter, sans-serif"
        fontSize={13}
        fontWeight={700}
        fill="#191c1e"
      >
        {id}
      </text>
    </g>
  );
}

/* ── Link form row ────────────────────────────────────────────────────────── */

interface LinkFormRow {
  from_node: string;
  to_node: string;
  free_flow_cost: string;
  capacity: string;
}

function emptyLink(): LinkFormRow {
  return { from_node: '', to_node: '', free_flow_cost: '', capacity: '' };
}

/* ── Demand form row ──────────────────────────────────────────────────────── */

interface DemandFormRow {
  origin: string;
  destination: string;
  demand: string;
}

function emptyDemand(): DemandFormRow {
  return { origin: '', destination: '', demand: '' };
}

/* ── Summary card ─────────────────────────────────────────────────────────── */

function SummaryCard({
  icon,
  label,
  value,
  valueColor,
}: {
  icon: string;
  label: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div className="bg-surface-container-low rounded-lg p-4 flex flex-col items-center gap-1.5">
      <span className="material-symbols-outlined text-xl text-primary">
        {icon}
      </span>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
        {label}
      </p>
      <p
        className="font-sans text-sm font-semibold"
        style={{ color: valueColor ?? '#191c1e' }}
      >
        {value}
      </p>
    </div>
  );
}

/* ── Main component ───────────────────────────────────────────────────────── */

export function SupernetworkFlowDiagram() {
  /* Form state */
  const [links, setLinks] = useState<LinkFormRow[]>([
    { from_node: '1', to_node: '2', free_flow_cost: '10', capacity: '100' },
    { from_node: '2', to_node: '3', free_flow_cost: '15', capacity: '80' },
    { from_node: '1', to_node: '3', free_flow_cost: '30', capacity: '60' },
  ]);
  const [demands, setDemands] = useState<DemandFormRow[]>([
    { origin: '1', destination: '3', demand: '50' },
  ]);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SupernetworkResponse | null>(null);

  /* ── Link management ────────────────────────────────────────────────────── */

  const updateLink = useCallback(
    (index: number, field: keyof LinkFormRow, value: string) => {
      setLinks((prev) => {
        const next = [...prev];
        next[index] = { ...next[index], [field]: value };
        return next;
      });
    },
    [],
  );

  const addLink = useCallback(() => {
    setLinks((prev) => [...prev, emptyLink()]);
  }, []);

  const removeLink = useCallback((index: number) => {
    setLinks((prev) => prev.filter((_, i) => i !== index));
  }, []);

  /* ── Demand management ──────────────────────────────────────────────────── */

  const updateDemand = useCallback(
    (index: number, field: keyof DemandFormRow, value: string) => {
      setDemands((prev) => {
        const next = [...prev];
        next[index] = { ...next[index], [field]: value };
        return next;
      });
    },
    [],
  );

  const addDemand = useCallback(() => {
    setDemands((prev) => [...prev, emptyDemand()]);
  }, []);

  const removeDemand = useCallback((index: number) => {
    setDemands((prev) => prev.filter((_, i) => i !== index));
  }, []);

  /* ── Validation ─────────────────────────────────────────────────────────── */

  const canCompute = useMemo(() => {
    if (links.length === 0 || demands.length === 0) return false;
    const linksValid = links.every(
      (l) =>
        l.from_node.trim() !== '' &&
        l.to_node.trim() !== '' &&
        !isNaN(parseFloat(l.free_flow_cost)) &&
        !isNaN(parseFloat(l.capacity)) &&
        parseFloat(l.capacity) > 0,
    );
    const demandsValid = demands.every(
      (d) =>
        d.origin.trim() !== '' &&
        d.destination.trim() !== '' &&
        !isNaN(parseFloat(d.demand)) &&
        parseFloat(d.demand) > 0,
    );
    return linksValid && demandsValid;
  }, [links, demands]);

  /* ── Compute ────────────────────────────────────────────────────────────── */

  const handleCompute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const parsedLinks: SupernetworkLink[] = links.map((l) => ({
        from_node: parseInt(l.from_node, 10),
        to_node: parseInt(l.to_node, 10),
        free_flow_cost: parseFloat(l.free_flow_cost),
        capacity: parseFloat(l.capacity),
      }));

      const parsedDemands: SupernetworkDemand[] = demands.map((d) => ({
        origin: parseInt(d.origin, 10),
        destination: parseInt(d.destination, 10),
        demand: parseFloat(d.demand),
      }));

      const res = await computeSupernetworkEquilibrium({
        links: parsedLinks,
        od_demands: parsedDemands,
      });
      setResult(res);
    } catch (err) {
      setError(
        extractApiError(
          err,
          "Erreur lors du calcul de l'equilibre supernetwork",
        ),
      );
    } finally {
      setLoading(false);
    }
  }, [links, demands]);

  /* ── SVG data ───────────────────────────────────────────────────────────── */

  const svgData = useMemo(() => {
    if (!result) return null;

    const allLinks = result.link_flows.map((lf) => ({
      from_node: lf.from_node,
      to_node: lf.to_node,
    }));

    const allDemands = demands.map((d) => ({
      origin: parseInt(d.origin, 10),
      destination: parseInt(d.destination, 10),
    }));

    const positions = computeNodePositions(allLinks, allDemands);
    const maxFlow = Math.max(...result.link_flows.map((lf) => lf.flow), 1);

    return { positions, maxFlow, flows: result.link_flows };
  }, [result, demands]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          hub
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Equilibre supernetwork (Frank-Wolfe)
        </h3>
      </div>

      {/* Links table */}
      <div className="mb-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
          Liens du reseau
        </p>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Noeud depart
                </th>
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Noeud arrivee
                </th>
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Cout libre
                </th>
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Capacite
                </th>
                <th className="w-10" />
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {links.map((link, idx) => (
                <tr key={idx} className="hover:bg-surface-bright">
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      value={link.from_node}
                      onChange={(e) =>
                        updateLink(idx, 'from_node', e.target.value)
                      }
                      placeholder="1"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      value={link.to_node}
                      onChange={(e) =>
                        updateLink(idx, 'to_node', e.target.value)
                      }
                      placeholder="2"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      step="0.1"
                      value={link.free_flow_cost}
                      onChange={(e) =>
                        updateLink(idx, 'free_flow_cost', e.target.value)
                      }
                      placeholder="10"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      step="1"
                      value={link.capacity}
                      onChange={(e) =>
                        updateLink(idx, 'capacity', e.target.value)
                      }
                      placeholder="100"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-2 py-1.5 text-center">
                    <button
                      type="button"
                      onClick={() => removeLink(idx)}
                      disabled={links.length <= 1}
                      className="text-on-surface-variant hover:text-error disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                      title="Supprimer"
                    >
                      <span className="material-symbols-outlined text-lg">
                        close
                      </span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <button
          type="button"
          onClick={addLink}
          className="mt-2 inline-flex items-center gap-1.5 text-primary text-sm font-medium hover:opacity-80 transition-opacity"
        >
          <span className="material-symbols-outlined text-base">add</span>
          Ajouter un lien
        </button>
      </div>

      {/* Demands table */}
      <div className="mb-5">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
          Demandes OD
        </p>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Origine
                </th>
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Destination
                </th>
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Demande
                </th>
                <th className="w-10" />
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {demands.map((dem, idx) => (
                <tr key={idx} className="hover:bg-surface-bright">
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      value={dem.origin}
                      onChange={(e) =>
                        updateDemand(idx, 'origin', e.target.value)
                      }
                      placeholder="1"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      value={dem.destination}
                      onChange={(e) =>
                        updateDemand(idx, 'destination', e.target.value)
                      }
                      placeholder="3"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      step="1"
                      value={dem.demand}
                      onChange={(e) =>
                        updateDemand(idx, 'demand', e.target.value)
                      }
                      placeholder="50"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-2 py-1.5 text-center">
                    <button
                      type="button"
                      onClick={() => removeDemand(idx)}
                      disabled={demands.length <= 1}
                      className="text-on-surface-variant hover:text-error disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                      title="Supprimer"
                    >
                      <span className="material-symbols-outlined text-lg">
                        close
                      </span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <button
          type="button"
          onClick={addDemand}
          className="mt-2 inline-flex items-center gap-1.5 text-primary text-sm font-medium hover:opacity-80 transition-opacity"
        >
          <span className="material-symbols-outlined text-base">add</span>
          Ajouter une demande
        </button>
      </div>

      {/* Compute button */}
      <button
        type="button"
        onClick={handleCompute}
        disabled={loading || !canCompute}
        className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-base">
              progress_activity
            </span>
            Calcul en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-base">
              calculate
            </span>
            Calculer Equilibre
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
      {result && !loading && svgData && (
        <div className="mt-6 space-y-6">
          {/* Summary cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <SummaryCard
              icon="payments"
              label="Cout systeme total"
              value={fmtMAD(result.total_system_cost)}
            />
            <SummaryCard
              icon="repeat"
              label="Iterations"
              value={madFmt.format(result.iterations)}
            />
            <SummaryCard
              icon={result.converged ? 'check_circle' : 'warning'}
              label="Convergence"
              value={result.converged ? 'Oui' : 'Non'}
              valueColor={result.converged ? '#22c55e' : '#ea580c'}
            />
            <SummaryCard
              icon="trending_down"
              label="Gap"
              value={result.gap < 0.001 ? '< 0.001' : madFmt.format(result.gap)}
            />
          </div>

          {/* SVG Network diagram */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Diagramme de flux
            </p>
            <div className="bg-surface-container-low rounded-xl border border-outline-variant/10 p-4 overflow-x-auto">
              <svg
                viewBox="0 0 600 400"
                className="w-full max-w-[600px] mx-auto"
                style={{ minHeight: 300 }}
              >
                <ArrowDefs />

                {/* Edges */}
                {svgData.flows.map((lf: LinkFlow, idx: number) => {
                  const from = getNodePos(svgData.positions, lf.from_node);
                  const to = getNodePos(svgData.positions, lf.to_node);
                  return (
                    <FlowEdge
                      key={`e-${idx}`}
                      from={from}
                      to={to}
                      flow={lf.flow}
                      cost={lf.cost}
                      maxFlow={svgData.maxFlow}
                    />
                  );
                })}

                {/* Nodes */}
                {svgData.positions.map((pos: NodePosition) => (
                  <NetworkNode
                    key={`n-${pos.id}`}
                    id={pos.id}
                    x={pos.x}
                    y={pos.y}
                  />
                ))}
              </svg>
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-6 mt-3 text-xs text-on-surface-variant">
              <span>
                Etiquettes:{' '}
                <strong className="text-on-surface">flux</strong> (cout)
              </span>
              <span>
                Epaisseur proportionnelle au flux
              </span>
            </div>
          </div>

          {/* Flow details table */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
              Detail des flux par lien
            </p>
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-surface-container-low/50">
                    <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      De
                    </th>
                    <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Vers
                    </th>
                    <th className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Flux
                    </th>
                    <th className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Cout
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/10">
                  {result.link_flows.map((lf: LinkFlow, idx: number) => (
                    <tr key={idx} className="hover:bg-surface-bright">
                      <td className="px-3 py-2 font-sans text-on-surface">
                        Noeud {lf.from_node}
                      </td>
                      <td className="px-3 py-2 font-sans text-on-surface">
                        Noeud {lf.to_node}
                      </td>
                      <td className="px-3 py-2 text-right font-sans font-medium text-on-surface">
                        {madFmt.format(lf.flow)}
                      </td>
                      <td className="px-3 py-2 text-right font-sans font-medium text-on-surface">
                        {fmtMAD(lf.cost)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="mt-6 flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            hub
          </span>
          <p className="text-sm">
            Definissez les liens et demandes, puis cliquez sur Calculer Equilibre.
          </p>
        </div>
      )}
    </div>
  );
}
