import { useState } from 'react';

/* ── Role configuration ─────────────────────────────────────────────────────── */
interface RoleConfig {
  name: string;
  label: string;
  icon: string;
  description: string;
  color: string;
  modules: string[];
  userCount: number;
}

const ROLES_CONFIG: RoleConfig[] = [
  { name: 'admin', label: 'Administrateur', icon: 'admin_panel_settings', description: 'Acces complet a la plateforme', color: '#0058be', modules: ['M1-M8', 'Admin'], userCount: 2 },
  { name: 'drh', label: 'DRH', icon: 'diversity_3', description: 'Gestion RH et mobilite (M1-M7)', color: '#2a9d8f', modules: ['M1', 'M2', 'M3', 'M4', 'M6', 'M7'], userCount: 5 },
  { name: 'daf', label: 'DAF', icon: 'account_balance', description: 'Finance et budgets (M2, M5-M7)', color: '#e9c46a', modules: ['M2', 'M5', 'M6', 'M7'], userCount: 3 },
  { name: 'responsable_parc', label: 'Responsable Parc', icon: 'garage', description: 'Gestion flotte et technologies (M2-M4)', color: '#264653', modules: ['M2', 'M3', 'M4'], userCount: 4 },
  { name: 'responsable_exploitation', label: 'Resp. Exploitation', icon: 'monitoring', description: 'Performance et temps reel (M1, M4, M8)', color: '#f4a261', modules: ['M1', 'M4', 'M8'], userCount: 6 },
  { name: 'prestataire', label: 'Prestataire', icon: 'handshake', description: 'Portail operateur (lecture seule)', color: '#6a4c93', modules: ['Operateur'], userCount: 8 },
  { name: 'conducteur', label: 'Conducteur', icon: 'directions_bus', description: 'Routes assignees et app mobile', color: '#e63946', modules: ['M8 (limite)'], userCount: 45 },
  { name: 'salarie', label: 'Salarie', icon: 'person', description: 'Profil et trajets personnels', color: '#457b9d', modules: ['Mobile'], userCount: 1200 },
  { name: 'operateur', label: 'Operateur', icon: 'engineering', description: 'Operations terrain (M8 lecture)', color: '#a8dadc', modules: ['M8 (lecture)'], userCount: 12 },
];

const HIERARCHY_LEVELS = [
  { level: 1, label: 'Administration', roles: ['admin'] },
  { level: 2, label: 'Direction', roles: ['drh', 'daf'] },
  { level: 3, label: 'Management', roles: ['responsable_parc', 'responsable_exploitation'] },
  { level: 4, label: 'Externe', roles: ['prestataire', 'operateur'] },
  { level: 5, label: 'Utilisateur', roles: ['conducteur', 'salarie'] },
];

/* ── Component ──────────────────────────────────────────────────────────────── */
export default function RoleManagementPage() {
  const [search, setSearch] = useState('');

  const filteredRoles = ROLES_CONFIG.filter((r) =>
    r.label.toLowerCase().includes(search.toLowerCase()) ||
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.description.toLowerCase().includes(search.toLowerCase())
  );

  const totalUsers = ROLES_CONFIG.reduce((sum, r) => sum + r.userCount, 0);

  return (
    <div className="flex flex-col gap-6 p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Gestion des Roles</h1>
          <p className="text-sm text-on-surface-variant mt-1">
            9 roles configures pour {totalUsers} utilisateurs
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">
              search
            </span>
            <input
              type="text"
              placeholder="Rechercher un role..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 text-sm bg-surface-container-high/50 border-none rounded-lg focus:ring-2 focus:ring-primary/20 focus:outline-none w-64"
            />
          </div>
        </div>
      </div>

      {/* Info banner: hierarchy */}
      <div className="bg-primary/5 border border-primary/10 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <span className="material-symbols-outlined text-primary text-xl mt-0.5">info</span>
          <div className="flex-1">
            <p className="text-[10px] font-bold uppercase tracking-widest text-primary mb-2">
              Hierarchie des roles
            </p>
            <div className="flex flex-wrap gap-x-6 gap-y-2">
              {HIERARCHY_LEVELS.map((level) => (
                <div key={level.level} className="flex items-center gap-2">
                  <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-primary/10 text-primary text-[10px] font-bold">
                    {level.level}
                  </span>
                  <span className="text-xs font-medium text-on-surface">{level.label}</span>
                  <span className="text-xs text-on-surface-variant">
                    ({level.roles.map((r) => ROLES_CONFIG.find((rc) => rc.name === r)?.label).join(', ')})
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Role cards grid */}
      {filteredRoles.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2">search_off</span>
          <p className="text-sm">Aucun role ne correspond a votre recherche.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRoles.map((role) => (
            <RoleCard key={role.name} role={role} />
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Role card ──────────────────────────────────────────────────────────────── */
function RoleCard({ role }: { role: RoleConfig }) {
  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 flex flex-col gap-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
          style={{ backgroundColor: `${role.color}15` }}
        >
          <span
            className="material-symbols-outlined text-xl"
            style={{ color: role.color }}
          >
            {role.icon}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-on-surface truncate">{role.label}</h3>
          <p className="text-xs text-on-surface-variant mt-0.5">{role.description}</p>
        </div>
      </div>

      {/* Module badges */}
      <div>
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
          Modules autorises
        </p>
        <div className="flex flex-wrap gap-1.5">
          {role.modules.map((mod) => (
            <span
              key={mod}
              className="inline-flex items-center rounded-md px-2 py-0.5 text-[10px] font-medium"
              style={{
                backgroundColor: `${role.color}12`,
                color: role.color,
              }}
            >
              {mod}
            </span>
          ))}
        </div>
      </div>

      {/* Footer: user count + role key */}
      <div className="flex items-center justify-between pt-2 border-t border-outline-variant/10">
        <div className="flex items-center gap-1.5 text-xs text-on-surface-variant">
          <span className="material-symbols-outlined text-sm">group</span>
          <span>{role.userCount} utilisateur{role.userCount !== 1 ? 's' : ''}</span>
        </div>
        <code className="text-[10px] font-mono text-on-surface-variant bg-surface-container-high/50 rounded px-1.5 py-0.5">
          {role.name}
        </code>
      </div>
    </div>
  );
}
