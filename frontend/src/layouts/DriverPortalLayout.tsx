import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { useDriverStore } from '@/stores/driverStore';

/* ── Navigation items ──────────────────────────────────────────────────── */

interface DriverNavItem {
  path: string;
  label: string;
  icon: string;
  end?: boolean;
}

const NAV_ITEMS: DriverNavItem[] = [
  { path: '/driver', label: 'Mes Trajets', icon: 'trips', end: true },
  { path: '/driver/vehicle', label: 'Mon Vehicule', icon: 'directions_car' },
  { path: '/driver/risk', label: 'Mon Score', icon: 'speed' },
  { path: '/driver/schedule', label: 'Planning', icon: 'calendar_month' },
];

const FILL = {
  fontVariationSettings: "'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24",
};

/* ── Layout ────────────────────────────────────────────────────────────── */

export function DriverPortalLayout() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const vehicle = useDriverStore((s) => s.vehicle);
  const unreadNotifications = useDriverStore((s) => s.unreadNotifications);

  const displayName = user
    ? `${user.first_name} ${user.last_name}`
    : 'Conducteur';

  const now = new Date();
  const dateStr = now.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const timeStr = now.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen bg-surface">
      {/* ── Sidebar ─────────────────────────────────────────────────────── */}
      <aside
        className="fixed left-0 top-0 h-screen bg-slate-50 flex flex-col z-50"
        style={{ width: 240 }}
        data-testid="driver-sidebar"
      >
        {/* Logo */}
        <div className="px-4 pt-5 pb-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-on-primary text-xl">
              route
            </span>
          </div>
          <div className="flex flex-col flex-1 min-w-0">
            <span className="font-sans text-sm font-bold text-on-surface leading-tight">
              Transpop
            </span>
            <span className="font-sans text-xs text-on-surface-variant leading-tight">
              Portail Conducteur
            </span>
          </div>
        </div>

        <div className="mx-5 h-px bg-surface-container-high" />

        {/* Navigation */}
        <nav className="flex-1 flex flex-col gap-0.5 px-3 py-4">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
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
                      'material-symbols-outlined text-xl leading-none shrink-0',
                      isActive ? 'text-blue-700' : 'text-slate-400',
                    ].join(' ')}
                    style={isActive ? FILL : undefined}
                  >
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="mx-5 h-px bg-surface-container-high" />

        {/* Bottom: user + logout */}
        <div className="px-3 py-3 flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-full bg-primary-fixed flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-on-primary-fixed-variant text-lg">
                person
              </span>
            </div>
            <div className="flex flex-col min-w-0 flex-1">
              <span className="text-sm font-medium text-on-surface truncate">
                {displayName}
              </span>
              <span className="text-xs text-on-surface-variant capitalize truncate">
                Conducteur
              </span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-red-50 hover:text-error transition-colors w-full"
            data-testid="driver-logout-btn"
          >
            <span className="material-symbols-outlined text-xl leading-none text-slate-400">
              logout
            </span>
            <span>Deconnexion</span>
          </button>
        </div>
      </aside>

      {/* ── Content area ────────────────────────────────────────────────── */}
      <div
        className="flex-1 flex flex-col"
        style={{ marginLeft: 240 }}
      >
        {/* Header */}
        <header className="sticky top-0 z-40 h-16 bg-slate-50/80 backdrop-blur-md shadow-sm px-8 flex items-center justify-between">
          {/* Left: date/time */}
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-on-surface-variant text-xl">
              schedule
            </span>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-on-surface capitalize">
                {dateStr}
              </span>
              <span className="text-xs text-on-surface-variant">{timeStr}</span>
            </div>
          </div>

          {/* Right: vehicle badge + notifications + name */}
          <div className="flex items-center gap-3">
            {/* Active vehicle badge */}
            {vehicle && (
              <div className="flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1">
                <span className="material-symbols-outlined text-primary text-base">
                  directions_car
                </span>
                <span className="text-xs font-semibold text-primary">
                  {vehicle.plate}
                </span>
              </div>
            )}

            {/* Notification bell */}
            <button
              type="button"
              className="relative w-9 h-9 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition"
              data-testid="notification-bell"
            >
              <span className="material-symbols-outlined text-xl">
                notifications
              </span>
              {unreadNotifications > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] rounded-full bg-error flex items-center justify-center text-[10px] font-bold text-white px-1">
                  {unreadNotifications}
                </span>
              )}
            </button>

            <div className="w-px h-6 bg-surface-container-high" />

            {/* Driver name */}
            <span className="text-sm font-medium text-on-surface">
              {displayName}
            </span>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
