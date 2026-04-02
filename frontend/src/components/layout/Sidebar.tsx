import { useTranslation } from 'react-i18next';
import { NavLink } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

interface NavItem {
  key: string;
  path: string;
  labelKey: string;
  icon: string;
}

const navItems: NavItem[] = [
  { key: 'dashboard', path: '/dashboard', labelKey: 'nav.dashboard', icon: 'dashboard' },
  { key: 'sites', path: '/sites', labelKey: 'nav.sites', icon: 'location_on' },
  { key: 'employees', path: '/employees', labelKey: 'nav.employees', icon: 'group' },
  { key: 'modal-analysis', path: '/modal-analysis', labelKey: 'nav.modal_analysis', icon: 'bar_chart' },
  { key: 'import', path: '/import', labelKey: 'nav.import', icon: 'upload_file' },
  { key: 'vehicles', path: '/vehicles', labelKey: 'nav.vehicles', icon: 'directions_car' },
  { key: 'optimization', path: '/optimization', labelKey: 'nav.optimization', icon: 'route' },
  { key: 'scenarios', path: '/scenarios', labelKey: 'nav.scenarios', icon: 'cloud' },
  { key: 'financial', path: '/financial', labelKey: 'nav.financial', icon: 'payments' },
  { key: 'reports', path: '/reports', labelKey: 'nav.reports', icon: 'article' },
  { key: 'settings', path: '/settings', labelKey: 'nav.settings', icon: 'settings' },
];

export function Sidebar() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);

  const displayName = user
    ? `${user.first_name} ${user.last_name}`
    : '---';

  const displayRole = user?.role ?? '---';

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-50 flex flex-col z-50">
      {/* Logo section */}
      <div className="px-5 pt-6 pb-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-primary-container flex items-center justify-center flex-shrink-0">
          <span className="material-symbols-outlined text-on-primary text-xl">
            route
          </span>
        </div>
        <div className="flex flex-col">
          <span className="font-sans text-sm font-bold text-on-surface leading-tight">
            Transpop
          </span>
          <span className="font-sans text-xs text-on-surface-variant leading-tight">
            Mobility Admin
          </span>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-5 h-px bg-surface-container-high" />

      {/* Navigation */}
      <nav className="flex-1 flex flex-col gap-0.5 px-3 py-3 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
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
                <span
                  className={[
                    'material-symbols-outlined text-xl leading-none',
                    isActive ? 'text-blue-700' : 'text-slate-400',
                  ].join(' ')}
                  style={isActive ? { fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24" } : undefined}
                >
                  {item.icon}
                </span>
                <span>{t(item.labelKey)}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Divider */}
      <div className="mx-5 h-px bg-surface-container-high" />

      {/* User profile card */}
      <div className="px-4 py-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-primary-fixed flex items-center justify-center flex-shrink-0">
          <span className="material-symbols-outlined text-on-primary-fixed-variant text-lg">
            person
          </span>
        </div>
        <div className="flex flex-col min-w-0">
          <span className="text-sm font-medium text-on-surface truncate">
            {displayName}
          </span>
          <span className="text-xs text-on-surface-variant capitalize truncate">
            {displayRole}
          </span>
        </div>
      </div>
    </aside>
  );
}
