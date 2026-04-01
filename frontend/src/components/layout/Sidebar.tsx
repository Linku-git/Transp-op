import { useTranslation } from 'react-i18next';
import { NavLink } from 'react-router-dom';

interface NavItem {
  key: string;
  path: string;
  labelKey: string;
}

const navItems: NavItem[] = [
  { key: 'dashboard', path: '/dashboard', labelKey: 'nav.dashboard' },
  { key: 'sites', path: '/sites', labelKey: 'nav.sites' },
  { key: 'employees', path: '/employees', labelKey: 'nav.employees' },
  { key: 'vehicles', path: '/vehicles', labelKey: 'nav.vehicles' },
  { key: 'optimization', path: '/optimization', labelKey: 'nav.optimization' },
  { key: 'financial', path: '/financial', labelKey: 'nav.financial' },
  { key: 'reports', path: '/reports', labelKey: 'nav.reports' },
  { key: 'settings', path: '/settings', labelKey: 'nav.settings' },
];

export function Sidebar() {
  const { t } = useTranslation();

  return (
    <aside className="bg-surface-container-low w-64 min-h-screen p-6 flex flex-col">
      <div className="mb-8">
        <span className="font-display text-xl font-bold text-primary">
          {t('app.name')}
        </span>
      </div>

      <nav className="flex flex-col gap-1">
        {navItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition',
                isActive
                  ? 'bg-surface-container text-secondary font-medium'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container',
              ].join(' ')
            }
          >
            <div className="w-5 h-5 rounded bg-surface-container-high flex-shrink-0" />
            <span>{t(item.labelKey)}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
