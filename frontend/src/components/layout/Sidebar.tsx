import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

/* ── Sub-item definition ──────────────────────────────────────────────────── */
interface SubItem {
  key: string;
  path: string;
  label: string;
  icon: string;
  end?: boolean;
}

/* ── Group definition ─────────────────────────────────────────────────────── */
interface NavGroup {
  key: string;
  label: string;
  icon: string;
  subs: SubItem[];
}

/* ── Single nav item ──────────────────────────────────────────────────────── */
interface NavItem {
  key: string;
  path: string;
  label: string;
  icon: string;
  end?: boolean;
}

/* ── Data ─────────────────────────────────────────────────────────────────── */
const TOP_ITEMS: NavItem[] = [
  { key: 'dashboard', path: '/dashboard', label: 'Dashboard', icon: 'dashboard', end: true },
  { key: 'map',       path: '/map',       label: 'Carte',     icon: 'map' },
];

const MASTER_GROUP: NavGroup = {
  key: 'master',
  label: 'Master data',
  icon: 'dataset',
  subs: [
    { key: 'master-sites',       path: '/sites',            label: 'Sites',                            icon: 'location_on' },
    { key: 'master-stops',       path: '/fleet/stops',      label: "Points d'Arrêt",                  icon: 'directions_bus' },
    { key: 'master-employees',   path: '/employees',        label: 'Employés',                         icon: 'group' },
    { key: 'master-consumption', path: '/fleet/consumption',label: 'Type Véhicules & Conso.',          icon: 'local_gas_station' },
    { key: 'master-vehicles',    path: '/vehicles',         label: 'Parc Véhicule',                    icon: 'directions_car', end: true },
    { key: 'master-config',      path: '/fleet/config',     label: 'Configuration Transport',          icon: 'settings_applications' },
  ],
};

const OPTIM_GROUP: NavGroup = {
  key: 'optimisation',
  label: 'Optimisation',
  icon: 'bolt',
  subs: [
    { key: 'opt-stops', path: '/optimization/stops',  label: 'Arrêts & Clusters',      icon: 'location_on' },
    { key: 'opt-fleet', path: '/optimization/fleet',  label: 'Optimisation Flotte',    icon: 'directions_bus' },
    { key: 'opt-routes',path: '/optimization/routes', label: 'Visualisation Routes',   icon: 'route' },
  ],
};

const OUTILS_GROUP: NavGroup = {
  key: 'outils',
  label: 'Outils',
  icon: 'build',
  subs: [
    { key: 'outils-modal',      path: '/modal-analysis', label: 'Analyse Modale',  icon: 'bar_chart' },
    { key: 'outils-financial',  path: '/financial',      label: 'Finance',         icon: 'payments' },
    { key: 'outils-scenarios',  path: '/scenarios',      label: 'Scénarios',       icon: 'cloud' },
    { key: 'outils-reports',    path: '/reports',        label: 'Rapports',        icon: 'article' },
    { key: 'outils-import',     path: '/import',         label: 'Import',          icon: 'upload_file' },
  ],
};

const SETTINGS_ITEM: NavItem = {
  key: 'settings', path: '/settings', label: 'Paramètres', icon: 'settings',
};

/* ── helpers ──────────────────────────────────────────────────────────────── */
function isGroupActive(group: NavGroup, pathname: string) {
  return group.subs.some((s) =>
    s.end ? pathname === s.path : pathname === s.path || pathname.startsWith(s.path + '/')
  );
}

const FILL_STYLE = { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24" };
const FILL_SM    = { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 20" };

/* ══════════════════════════════════════════════════════════════════════════════
   Expanded sub-list
══════════════════════════════════════════════════════════════════════════════ */
function ExpandedSubList({ subs }: { subs: SubItem[] }) {
  return (
    <div className="ml-8 flex flex-col gap-0.5">
      {subs.map((sub) => (
        <NavLink
          key={sub.key}
          to={sub.path}
          end={sub.end}
          className={({ isActive }) =>
            [
              'flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
              isActive
                ? 'bg-blue-50 text-blue-700'
                : 'text-slate-500 hover:bg-slate-200 hover:text-slate-800',
            ].join(' ')
          }
        >
          {({ isActive }) => (
            <>
              <span
                className={['material-symbols-outlined text-sm leading-none', isActive ? 'text-blue-600' : 'text-slate-400'].join(' ')}
                style={isActive ? FILL_SM : undefined}
              >
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
   Collapsed sub-list  (tree: vertical line + horizontal connectors)
══════════════════════════════════════════════════════════════════════════════ */
function CollapsedSubTree({ subs }: { subs: SubItem[] }) {
  return (
    <div className="relative flex flex-col items-center w-full">
      {/* vertical guide line */}
      <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-px bg-slate-200 pointer-events-none" />
      {subs.map((sub, idx) => (
        <div key={sub.key} className="relative flex items-center w-full justify-center py-0.5">
          {/* horizontal connector */}
          <div className="absolute left-1/2 top-1/2 -translate-y-1/2 w-2 h-px bg-slate-200 pointer-events-none"
            style={{ left: 'calc(50% + 1px)' }} />
          <NavLink
            to={sub.path}
            end={sub.end}
            title={sub.label}
            className={({ isActive }) =>
              [
                'z-10 flex items-center justify-center rounded-md transition-colors',
                'w-7 h-7 ml-2',
                isActive
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-slate-400 hover:bg-slate-200 hover:text-slate-700',
              ].join(' ')
            }
            style={{ marginLeft: 4 }}
          >
            {({ isActive }) => (
              <span
                className="material-symbols-outlined text-sm leading-none"
                style={isActive ? FILL_SM : undefined}
              >
                {sub.icon}
              </span>
            )}
          </NavLink>
        </div>
      ))}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   Collapsed group button + optional sub-tree
══════════════════════════════════════════════════════════════════════════════ */
function CollapsedGroup({
  group, pathname,
}: { group: NavGroup; pathname: string }) {
  const active = isGroupActive(group, pathname);
  const [open, setOpen] = useState(active);

  return (
    <>
      <button
        title={group.label}
        onClick={() => setOpen((o) => !o)}
        className={[
          'flex items-center justify-center rounded-lg w-full py-2 transition-colors',
          active ? 'bg-blue-50 text-blue-700' : 'text-slate-400 hover:bg-slate-200 hover:text-slate-900',
        ].join(' ')}
      >
        <span
          className="material-symbols-outlined text-xl leading-none"
          style={active ? FILL_STYLE : undefined}
        >
          {group.icon}
        </span>
      </button>
      {open && <CollapsedSubTree subs={group.subs} />}
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   Expanded group button + optional sub-list
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
          style={active ? FILL_STYLE : undefined}
        >
          {group.icon}
        </span>
        <span className="flex-1 text-left">{group.label}</span>
        <span
          className={[
            'material-symbols-outlined text-base leading-none transition-transform duration-200',
            active ? 'text-blue-500' : 'text-slate-400',
            open ? 'rotate-180' : '',
          ].join(' ')}
        >
          expand_more
        </span>
      </button>
      {open && <ExpandedSubList subs={group.subs} />}
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   Main Sidebar
══════════════════════════════════════════════════════════════════════════════ */
interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { pathname } = useLocation();
  const user = useAuthStore((s) => s.user);
  const displayName = user ? `${user.first_name} ${user.last_name}` : '---';
  const displayRole = user?.role ?? '---';

  /* ── collapsed ─────────────────────────────────────────────────────────── */
  if (collapsed) {
    return (
      <aside
        className="fixed left-0 top-0 h-screen bg-slate-50 flex flex-col z-50 transition-[width] duration-300 overflow-hidden"
        style={{ width: 56 }}
      >
        <div className="flex items-center justify-center pt-5 pb-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-on-primary text-lg">route</span>
          </div>
        </div>

        <div className="mx-2 h-px bg-surface-container-high" />

        <nav className="flex-1 flex flex-col items-center gap-0.5 py-3 overflow-y-auto">
          {TOP_ITEMS.map((item) => {
            const active = item.end ? pathname === item.path : pathname.startsWith(item.path);
            return (
              <NavLink
                key={item.key}
                to={item.path}
                end={item.end}
                title={item.label}
                className={[
                  'flex items-center justify-center rounded-lg w-full py-2 transition-colors',
                  active ? 'bg-blue-50 text-blue-700' : 'text-slate-400 hover:bg-slate-200 hover:text-slate-900',
                ].join(' ')}
              >
                <span
                  className="material-symbols-outlined text-xl leading-none"
                  style={active ? FILL_STYLE : undefined}
                >
                  {item.icon}
                </span>
              </NavLink>
            );
          })}

          <CollapsedGroup group={MASTER_GROUP} pathname={pathname} />
          <CollapsedGroup group={OPTIM_GROUP} pathname={pathname} />
          <CollapsedGroup group={OUTILS_GROUP} pathname={pathname} />

          {(() => {
            const active = pathname.startsWith(SETTINGS_ITEM.path);
            return (
              <NavLink
                to={SETTINGS_ITEM.path}
                title={SETTINGS_ITEM.label}
                className={[
                  'flex items-center justify-center rounded-lg w-full py-2 transition-colors',
                  active ? 'bg-blue-50 text-blue-700' : 'text-slate-400 hover:bg-slate-200 hover:text-slate-900',
                ].join(' ')}
              >
                <span
                  className="material-symbols-outlined text-xl leading-none"
                  style={active ? FILL_STYLE : undefined}
                >
                  {SETTINGS_ITEM.icon}
                </span>
              </NavLink>
            );
          })()}
        </nav>

        <div className="mx-2 h-px bg-surface-container-high" />

        <div className="flex flex-col items-center py-3 gap-2">
          <button
            onClick={onToggle}
            title="Étendre le menu"
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-200 text-slate-400 transition-colors"
          >
            <span className="material-symbols-outlined text-xl">chevron_right</span>
          </button>
          <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center shrink-0" title={displayName}>
            <span className="material-symbols-outlined text-on-primary-fixed-variant text-base">person</span>
          </div>
        </div>
      </aside>
    );
  }

  /* ── expanded ──────────────────────────────────────────────────────────── */
  const itemCls = (active: boolean) =>
    [
      'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
      active ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900',
    ].join(' ');

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-50 flex flex-col z-50 transition-[width] duration-300">
      <div className="px-4 pt-5 pb-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-on-primary text-xl">route</span>
        </div>
        <div className="flex flex-col flex-1 min-w-0">
          <span className="font-sans text-sm font-bold text-on-surface leading-tight">Transpop</span>
          <span className="font-sans text-xs text-on-surface-variant leading-tight">Mobility Admin</span>
        </div>
        <button
          onClick={onToggle}
          title="Réduire le menu"
          className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors shrink-0"
        >
          <span className="material-symbols-outlined text-lg leading-none">chevron_left</span>
        </button>
      </div>

      <div className="mx-5 h-px bg-surface-container-high" />

      <nav className="flex-1 flex flex-col gap-0.5 px-3 py-3 overflow-y-auto">
        {TOP_ITEMS.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end={item.end}
            className={({ isActive }) => itemCls(isActive)}
          >
            {({ isActive }) => (
              <>
                <span
                  className={['material-symbols-outlined text-xl leading-none shrink-0', isActive ? 'text-blue-700' : 'text-slate-400'].join(' ')}
                  style={isActive ? FILL_STYLE : undefined}
                >
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}

        <ExpandedGroup group={MASTER_GROUP} pathname={pathname} />
        <ExpandedGroup group={OPTIM_GROUP} pathname={pathname} />
        <ExpandedGroup group={OUTILS_GROUP} pathname={pathname} />

        <NavLink
          to={SETTINGS_ITEM.path}
          className={({ isActive }) => itemCls(isActive)}
        >
          {({ isActive }) => (
            <>
              <span
                className={['material-symbols-outlined text-xl leading-none shrink-0', isActive ? 'text-blue-700' : 'text-slate-400'].join(' ')}
                style={isActive ? FILL_STYLE : undefined}
              >
                {SETTINGS_ITEM.icon}
              </span>
              <span>{SETTINGS_ITEM.label}</span>
            </>
          )}
        </NavLink>
      </nav>

      <div className="mx-5 h-px bg-surface-container-high" />

      <div className="px-4 py-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-primary-fixed flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-on-primary-fixed-variant text-lg">person</span>
        </div>
        <div className="flex flex-col min-w-0">
          <span className="text-sm font-medium text-on-surface truncate">{displayName}</span>
          <span className="text-xs text-on-surface-variant capitalize truncate">{displayRole}</span>
        </div>
      </div>
    </aside>
  );
}
