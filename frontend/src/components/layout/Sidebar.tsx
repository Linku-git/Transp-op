import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

/* ── Types ──────────────────────────────────────────────────────────────────── */
interface SubItem { key: string; path: string; label: string; icon: string; end?: boolean; }
interface NavGroup { key: string; label: string; icon: string; subs: SubItem[]; }
interface NavItem  { key: string; path: string; label: string; icon: string; end?: boolean; }

/* ── Navigation data ─────────────────────────────────────────────────────────── */
const TOP_ITEMS: NavItem[] = [
  { key: 'dashboard', path: '/dashboard', label: 'Dashboard', icon: 'dashboard', end: true },
  { key: 'map',       path: '/map',       label: 'Carte',     icon: 'map' },
];

const MASTER_GROUP: NavGroup = {
  key: 'master', label: 'Master data', icon: 'dataset',
  subs: [
    { key: 'master-sites',       path: '/sites',             label: 'Sites',                       icon: 'location_on' },
    { key: 'master-stops',       path: '/fleet/stops',       label: "Points d'Arrêt",              icon: 'directions_bus' },
    { key: 'master-employees',   path: '/employees',         label: 'Employés',                    icon: 'group' },
    { key: 'master-consumption', path: '/fleet/consumption', label: 'Véhicules & Conso.',          icon: 'local_gas_station' },
    { key: 'master-vehicles',    path: '/vehicles',          label: 'Parc Véhicule',               icon: 'directions_car', end: true },
    { key: 'master-config',      path: '/fleet/config',      label: 'Config. Transport',           icon: 'settings_applications' },
  ],
};

const OPTIM_GROUP: NavGroup = {
  key: 'optimisation', label: 'Optimisation', icon: 'bolt',
  subs: [
    { key: 'opt-stops',  path: '/optimization/stops',  label: 'Arrêts & Clusters',   icon: 'location_on' },
    { key: 'opt-fleet',  path: '/optimization/fleet',  label: 'Optimisation Flotte', icon: 'directions_bus' },
    { key: 'opt-routes', path: '/optimization/routes', label: 'Visualisation Routes',icon: 'route' },
  ],
};

const SOTREG_GROUP: NavGroup = {
  key: 'sotreg', label: 'SOTREG', icon: 'analytics',
  subs: [
    { key: 'sotreg-diagnostic', path: '/sotreg',              label: 'Diagnostic Flotte', icon: 'monitoring', end: true },
    { key: 'sotreg-lignes',     path: '/sotreg/lignes',       label: 'Lignes Transport',  icon: 'route' },
  ],
};

const OUTILS_GROUP: NavGroup = {
  key: 'outils', label: 'Outils', icon: 'build',
  subs: [
    { key: 'outils-modal',     path: '/modal-analysis', label: 'Analyse Modale', icon: 'bar_chart' },
    { key: 'outils-financial', path: '/financial',      label: 'Finance',        icon: 'payments' },
    { key: 'outils-scenarios', path: '/scenarios',      label: 'Scénarios',      icon: 'cloud' },
    { key: 'outils-content',  path: '/content',        label: 'Contenu',        icon: 'feed' },
    { key: 'outils-reports',   path: '/reports',        label: 'Rapports',       icon: 'article' },
    { key: 'outils-import',    path: '/import',         label: 'Import',         icon: 'upload_file' },
  ],
};

const SETTINGS_ITEM: NavItem = { key: 'settings', path: '/settings', label: 'Paramètres', icon: 'settings' };

/* ── Helpers ─────────────────────────────────────────────────────────────────── */
function isGroupActive(group: NavGroup, pathname: string) {
  return group.subs.some((s) =>
    s.end ? pathname === s.path : pathname === s.path || pathname.startsWith(s.path + '/')
  );
}

const FILL   = { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24" };
const FILL_S = { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 20" };

/* ══════════════════════════════════════════════════════════════════════════════
   EXPANDED — sub-list
══════════════════════════════════════════════════════════════════════════════ */
function ExpandedSubList({ subs }: { subs: SubItem[] }) {
  return (
    <div className="ml-8 flex flex-col gap-0.5">
      {subs.map((sub) => (
        <NavLink key={sub.key} to={sub.path} end={sub.end}
          className={({ isActive }) => [
            'flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
            isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-500 hover:bg-slate-200 hover:text-slate-800',
          ].join(' ')}
        >
          {({ isActive }) => (
            <>
              <span className={['material-symbols-outlined text-sm leading-none', isActive ? 'text-blue-600' : 'text-slate-400'].join(' ')} style={isActive ? FILL_S : undefined}>
                {sub.icon}
              </span>
              <span className="leading-tight">{sub.label}</span>
            </>
          )}
        </NavLink>
      ))}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   COLLAPSED — sub-item panel (left-accent bar + icon grid)
══════════════════════════════════════════════════════════════════════════════ */
function CollapsedSubPanel({ subs }: { subs: SubItem[] }) {
  return (
    <div className="relative w-full flex flex-col items-center gap-0.5 py-0.5">
      {/* left accent bar */}
      <div className="absolute left-3 top-0 bottom-0 w-0.5 rounded-full bg-blue-200 pointer-events-none" />
      {subs.map((sub) => (
        <NavLink
          key={sub.key}
          to={sub.path}
          end={sub.end}
          title={sub.label}
          className={({ isActive }) => [
            'relative z-10 flex items-center justify-center rounded-lg transition-colors',
            'w-9 h-9 ml-4',
            isActive
              ? 'bg-blue-100 text-blue-600'
              : 'text-slate-400 hover:bg-slate-200 hover:text-slate-700',
          ].join(' ')}
        >
          {({ isActive }) => (
            <span className="material-symbols-outlined text-[15px] leading-none" style={isActive ? FILL_S : undefined}>
              {sub.icon}
            </span>
          )}
        </NavLink>
      ))}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   COLLAPSED — group
══════════════════════════════════════════════════════════════════════════════ */
function CollapsedGroup({ group, pathname }: { group: NavGroup; pathname: string }) {
  const active = isGroupActive(group, pathname);
  const [open, setOpen] = useState(active);

  return (
    <>
      <button
        title={group.label}
        onClick={() => setOpen((o) => !o)}
        className={[
          'flex items-center justify-center rounded-lg w-full py-2.5 transition-colors',
          active ? 'bg-blue-50 text-blue-700' : 'text-slate-400 hover:bg-slate-200 hover:text-slate-900',
        ].join(' ')}
      >
        <span className="material-symbols-outlined text-xl leading-none" style={active ? FILL : undefined}>
          {group.icon}
        </span>
      </button>
      {open && <CollapsedSubPanel subs={group.subs} />}
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   EXPANDED — group
══════════════════════════════════════════════════════════════════════════════ */
function ExpandedGroup({ group, pathname }: { group: NavGroup; pathname: string }) {
  const active = isGroupActive(group, pathname);
  const [open, setOpen] = useState(active);

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        className={[
          'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors w-full text-left',
          active ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900',
        ].join(' ')}
      >
        <span
          className={['material-symbols-outlined text-xl leading-none shrink-0', active ? 'text-blue-700' : 'text-slate-400'].join(' ')}
          style={active ? FILL : undefined}
        >
          {group.icon}
        </span>
        <span className="flex-1 text-left">{group.label}</span>
        <span className={['material-symbols-outlined text-base leading-none transition-transform duration-200', active ? 'text-blue-500' : 'text-slate-400', open ? 'rotate-180' : ''].join(' ')}>
          expand_more
        </span>
      </button>
      {open && <ExpandedSubList subs={group.subs} />}
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════════════════════════ */
interface SidebarProps { collapsed: boolean; onToggle: () => void; }

const COLLAPSED_W = 68;
const EXPANDED_W  = 256;

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { pathname } = useLocation();
  const user = useAuthStore((s) => s.user);
  const displayName = user ? `${user.first_name} ${user.last_name}` : '---';
  const displayRole = user?.role ?? '---';

  /* ── COLLAPSED ──────────────────────────────────────────────────────────── */
  if (collapsed) {
    return (
      <aside
        className="fixed left-0 top-0 h-screen bg-slate-50 flex flex-col z-50 transition-[width] duration-300 overflow-hidden"
        style={{ width: COLLAPSED_W }}
      >
        {/* Logo */}
        <div className="flex items-center justify-center pt-5 pb-4">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-on-primary text-xl">route</span>
          </div>
        </div>

        <div className="mx-2 h-px bg-surface-container-high" />

        <nav className="flex-1 flex flex-col items-center gap-0.5 py-3 px-2 overflow-y-auto">
          {TOP_ITEMS.map((item) => {
            const active = item.end ? pathname === item.path : pathname.startsWith(item.path);
            return (
              <NavLink
                key={item.key}
                to={item.path}
                end={item.end}
                title={item.label}
                className={[
                  'flex items-center justify-center rounded-lg w-full py-2.5 transition-colors',
                  active ? 'bg-blue-50 text-blue-700' : 'text-slate-400 hover:bg-slate-200 hover:text-slate-900',
                ].join(' ')}
              >
                <span className="material-symbols-outlined text-xl leading-none" style={active ? FILL : undefined}>
                  {item.icon}
                </span>
              </NavLink>
            );
          })}

          <CollapsedGroup group={MASTER_GROUP} pathname={pathname} />
          <CollapsedGroup group={OPTIM_GROUP} pathname={pathname} />
          <CollapsedGroup group={SOTREG_GROUP} pathname={pathname} />
          <CollapsedGroup group={OUTILS_GROUP} pathname={pathname} />

          {(() => {
            const active = pathname.startsWith(SETTINGS_ITEM.path);
            return (
              <NavLink
                to={SETTINGS_ITEM.path}
                title={SETTINGS_ITEM.label}
                className={[
                  'flex items-center justify-center rounded-lg w-full py-2.5 transition-colors',
                  active ? 'bg-blue-50 text-blue-700' : 'text-slate-400 hover:bg-slate-200 hover:text-slate-900',
                ].join(' ')}
              >
                <span className="material-symbols-outlined text-xl leading-none" style={active ? FILL : undefined}>
                  {SETTINGS_ITEM.icon}
                </span>
              </NavLink>
            );
          })()}
        </nav>

        <div className="mx-2 h-px bg-surface-container-high" />

        {/* Bottom: expand button + avatar */}
        <div className="flex flex-col items-center py-3 gap-2">
          <button
            onClick={onToggle}
            title="Étendre le menu"
            className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-slate-200 text-slate-400 transition-colors"
          >
            <span className="material-symbols-outlined text-xl">chevron_right</span>
          </button>
          <div className="w-9 h-9 rounded-full bg-primary-fixed flex items-center justify-center shrink-0" title={displayName}>
            <span className="material-symbols-outlined text-on-primary-fixed-variant text-base">person</span>
          </div>
        </div>
      </aside>
    );
  }

  /* ── EXPANDED ───────────────────────────────────────────────────────────── */
  const itemCls = (active: boolean) =>
    [
      'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
      active ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900',
    ].join(' ');

  return (
    <aside
      className="fixed left-0 top-0 h-screen bg-slate-50 flex flex-col z-50 transition-[width] duration-300"
      style={{ width: EXPANDED_W }}
    >
      {/* Logo — no collapse button here any more */}
      <div className="px-4 pt-5 pb-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-on-primary text-xl">route</span>
        </div>
        <div className="flex flex-col flex-1 min-w-0">
          <span className="font-sans text-sm font-bold text-on-surface leading-tight">Transpop</span>
          <span className="font-sans text-xs text-on-surface-variant leading-tight">Mobility Admin</span>
        </div>
      </div>

      <div className="mx-5 h-px bg-surface-container-high" />

      <nav className="flex-1 flex flex-col gap-0.5 px-3 py-3 overflow-y-auto">
        {TOP_ITEMS.map((item) => (
          <NavLink key={item.key} to={item.path} end={item.end} className={({ isActive }) => itemCls(isActive)}>
            {({ isActive }) => (
              <>
                <span className={['material-symbols-outlined text-xl leading-none shrink-0', isActive ? 'text-blue-700' : 'text-slate-400'].join(' ')} style={isActive ? FILL : undefined}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}

        <ExpandedGroup group={MASTER_GROUP} pathname={pathname} />
        <ExpandedGroup group={OPTIM_GROUP} pathname={pathname} />
        <ExpandedGroup group={SOTREG_GROUP} pathname={pathname} />
        <ExpandedGroup group={OUTILS_GROUP} pathname={pathname} />

        <NavLink to={SETTINGS_ITEM.path} className={({ isActive }) => itemCls(isActive)}>
          {({ isActive }) => (
            <>
              <span className={['material-symbols-outlined text-xl leading-none shrink-0', isActive ? 'text-blue-700' : 'text-slate-400'].join(' ')} style={isActive ? FILL : undefined}>
                {SETTINGS_ITEM.icon}
              </span>
              <span>{SETTINGS_ITEM.label}</span>
            </>
          )}
        </NavLink>
      </nav>

      <div className="mx-5 h-px bg-surface-container-high" />

      {/* Bottom: user info + collapse button side by side */}
      <div className="px-3 py-3 flex items-center gap-2">
        <div className="w-9 h-9 rounded-full bg-primary-fixed flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-on-primary-fixed-variant text-lg">person</span>
        </div>
        <div className="flex flex-col min-w-0 flex-1">
          <span className="text-sm font-medium text-on-surface truncate">{displayName}</span>
          <span className="text-xs text-on-surface-variant capitalize truncate">{displayRole}</span>
        </div>
        <button
          onClick={onToggle}
          title="Réduire le menu"
          className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors shrink-0"
        >
          <span className="material-symbols-outlined text-lg leading-none">chevron_left</span>
        </button>
      </div>
    </aside>
  );
}
