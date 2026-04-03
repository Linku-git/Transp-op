import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

interface NavItem {
  key: string;
  path: string;
  labelKey: string;
  icon: string;
  exact?: boolean;
}

interface MasterSubItem {
  key: string;
  path: string;
  label: string;
  icon: string;
}

const topNavItems: NavItem[] = [
  { key: 'dashboard', path: '/dashboard', labelKey: 'nav.dashboard', icon: 'dashboard' },
  { key: 'map',       path: '/map',       labelKey: 'nav.map',       icon: 'map' },
];

const masterSubItems: MasterSubItem[] = [
  { key: 'master-sites',       path: '/sites',             label: 'Sites',                             icon: 'location_on' },
  { key: 'master-stops',       path: '/fleet/stops',       label: "Points d'Arrêt",                   icon: 'directions_bus' },
  { key: 'master-employees',   path: '/employees',          label: 'Employes',                          icon: 'group' },
  { key: 'master-consumption', path: '/fleet/consumption',  label: 'Type Véhicules & Consommation',    icon: 'local_gas_station' },
  { key: 'master-vehicles',    path: '/vehicles',           label: 'Parc Véhicule',                    icon: 'directions_car' },
  { key: 'master-config',      path: '/fleet/config',       label: 'Configuration Transport-Véhicule', icon: 'settings_applications' },
];

const bottomNavItems: NavItem[] = [
  { key: 'modal-analysis', path: '/modal-analysis', labelKey: 'nav.modal_analysis', icon: 'bar_chart' },
  { key: 'import',         path: '/import',         labelKey: 'nav.import',         icon: 'upload_file' },
  { key: 'optimization',   path: '/optimization',   labelKey: 'nav.optimization',   icon: 'route' },
  { key: 'scenarios',      path: '/scenarios',      labelKey: 'nav.scenarios',      icon: 'cloud' },
  { key: 'financial',      path: '/financial',      labelKey: 'nav.financial',      icon: 'payments' },
  { key: 'reports',        path: '/reports',        labelKey: 'nav.reports',        icon: 'article' },
  { key: 'settings',       path: '/settings',       labelKey: 'nav.settings',       icon: 'settings' },
];

const masterPaths = masterSubItems.map((i) => i.path);

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const user = useAuthStore((s) => s.user);

  const isMasterActive = masterPaths.some((p) =>
    p === '/vehicles'
      ? pathname === '/vehicles' || pathname.startsWith('/vehicles/')
      : pathname === p || pathname.startsWith(p + '/')
  );

  const [masterOpen, setMasterOpen] = useState(isMasterActive);

  const displayName = user ? `${user.first_name} ${user.last_name}` : '---';
  const displayRole = user?.role ?? '---';

  /* ── Helpers ── */
  const iconCls = (active: boolean) =>
    [
      'material-symbols-outlined text-xl leading-none shrink-0',
      active ? 'text-blue-700' : 'text-slate-400',
    ].join(' ');

  const iconStyle = (active: boolean) =>
    active
      ? { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24" }
      : undefined;

  const linkCls = (active: boolean) =>
    [
      'flex items-center rounded-lg transition-colors',
      collapsed ? 'justify-center px-0 py-2 w-full' : 'gap-3 px-3 py-2',
      active
        ? 'bg-blue-50 text-blue-700'
        : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900',
    ].join(' ');

  /* ── Collapsed view ── */
  if (collapsed) {
    return (
      <aside
        className="fixed left-0 top-0 h-screen bg-slate-50 flex flex-col z-50 transition-[width] duration-300 overflow-hidden"
        style={{ width: 56 }}
      >
        {/* Logo icon */}
        <div className="flex items-center justify-center pt-5 pb-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-on-primary text-lg">route</span>
          </div>
        </div>

        <div className="mx-2 h-px bg-surface-container-high" />

        <nav className="flex-1 flex flex-col items-center gap-0.5 py-3 overflow-y-auto">
          {/* Top items */}
          {topNavItems.map((item) => (
            <NavLink
              key={item.key}
              to={item.path}
              title={t(item.labelKey)}
              className={({ isActive }) => linkCls(isActive)}
            >
              {({ isActive }) => (
                <span className={iconCls(isActive)} style={iconStyle(isActive)}>
                  {item.icon}
                </span>
              )}
            </NavLink>
          ))}

          {/* Master data — icon only, shows all sub-items in a tooltip-style */}
          <button
            title="Master data"
            onClick={() => setMasterOpen((o) => !o)}
            className={[
              'flex items-center justify-center rounded-lg w-full py-2 transition-colors',
              isMasterActive
                ? 'bg-blue-50 text-blue-700'
                : 'text-slate-400 hover:bg-slate-200 hover:text-slate-900',
            ].join(' ')}
          >
            <span
              className="material-symbols-outlined text-xl leading-none"
              style={isMasterActive ? { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24" } : undefined}
            >
              dataset
            </span>
          </button>

          {masterOpen && (
            <div className="flex flex-col items-center gap-0.5 w-full">
              {masterSubItems.map((sub) => (
                <NavLink
                  key={sub.key}
                  to={sub.path}
                  end={sub.path === '/vehicles'}
                  title={sub.label}
                  className={({ isActive }) =>
                    [
                      'flex items-center justify-center rounded-lg w-full py-1.5 transition-colors',
                      isActive
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-slate-400 hover:bg-slate-200',
                    ].join(' ')
                  }
                >
                  {({ isActive }) => (
                    <span
                      className="material-symbols-outlined text-base leading-none"
                      style={isActive ? { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 20" } : undefined}
                    >
                      {sub.icon}
                    </span>
                  )}
                </NavLink>
              ))}
            </div>
          )}

          {/* Bottom items */}
          {bottomNavItems.map((item) => (
            <NavLink
              key={item.key}
              to={item.path}
              title={t(item.labelKey)}
              className={({ isActive }) => linkCls(isActive)}
            >
              {({ isActive }) => (
                <span className={iconCls(isActive)} style={iconStyle(isActive)}>
                  {item.icon}
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="mx-2 h-px bg-surface-container-high" />

        {/* Expand toggle */}
        <div className="flex flex-col items-center py-3 gap-2">
          <button
            onClick={onToggle}
            title="Étendre le menu"
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-200 text-slate-400 transition-colors"
          >
            <span className="material-symbols-outlined text-xl">chevron_right</span>
          </button>
          {/* User avatar */}
          <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center shrink-0" title={displayName}>
            <span className="material-symbols-outlined text-on-primary-fixed-variant text-base">person</span>
          </div>
        </div>
      </aside>
    );
  }

  /* ── Expanded view ── */
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-50 flex flex-col z-50 transition-[width] duration-300">
      {/* Logo + collapse button */}
      <div className="px-4 pt-5 pb-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-on-primary text-xl">route</span>
        </div>
        <div className="flex flex-col flex-1 min-w-0">
          <span className="font-sans text-sm font-bold text-on-surface leading-tight">Transpop</span>
          <span className="font-sans text-xs text-on-surface-variant leading-tight">Mobility Admin</span>
        </div>
        {/* Collapse toggle */}
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

        {/* Top items */}
        {topNavItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end={item.exact}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900',
              ].join(' ')
            }
          >
            {({ isActive }) => (
              <>
                <span className={iconCls(isActive)} style={iconStyle(isActive)}>
                  {item.icon}
                </span>
                <span>{t(item.labelKey)}</span>
              </>
            )}
          </NavLink>
        ))}

        {/* Master data collapsible */}
        <button
          onClick={() => setMasterOpen((o) => !o)}
          className={[
            'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors w-full text-left',
            isMasterActive
              ? 'bg-blue-50 text-blue-700'
              : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900',
          ].join(' ')}
        >
          <span
            className={iconCls(isMasterActive)}
            style={isMasterActive ? { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24" } : undefined}
          >
            dataset
          </span>
          <span className="flex-1 text-left">Master data</span>
          <span
            className={[
              'material-symbols-outlined text-base leading-none transition-transform duration-200',
              isMasterActive ? 'text-blue-500' : 'text-slate-400',
              masterOpen ? 'rotate-180' : '',
            ].join(' ')}
          >
            expand_more
          </span>
        </button>

        {masterOpen && (
          <div className="ml-8 flex flex-col gap-0.5">
            {masterSubItems.map((sub) => (
              <NavLink
                key={sub.key}
                to={sub.path}
                end={sub.path === '/vehicles'}
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
                      className={[
                        'material-symbols-outlined text-sm leading-none',
                        isActive ? 'text-blue-600' : 'text-slate-400',
                      ].join(' ')}
                      style={isActive ? { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 20" } : undefined}
                    >
                      {sub.icon}
                    </span>
                    <span className="leading-tight">{sub.label}</span>
                  </>
                )}
              </NavLink>
            ))}
          </div>
        )}

        {/* Bottom nav items */}
        {bottomNavItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end={item.exact}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900',
              ].join(' ')
            }
          >
            {({ isActive }) => (
              <>
                <span className={iconCls(isActive)} style={iconStyle(isActive)}>
                  {item.icon}
                </span>
                <span>{t(item.labelKey)}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="mx-5 h-px bg-surface-container-high" />

      {/* User profile */}
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
