import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/stores/authStore';

export function Header() {
  const { t, i18n } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const toggleLanguage = () => {
    const next = i18n.language === 'fr' ? 'en' : 'fr';
    i18n.changeLanguage(next);
  };

  const displayName = user
    ? `${user.first_name} ${user.last_name}`
    : '---';

  return (
    <header className="sticky top-0 z-40 h-16 bg-slate-50/80 backdrop-blur-md shadow-sm px-8 flex items-center justify-between">
      {/* Left side: search bar */}
      <div className="flex items-center gap-4">
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-xl">
            search
          </span>
          <input
            type="text"
            placeholder={t('header.search_placeholder', 'Rechercher...')}
            className="h-9 w-72 rounded-full bg-surface-container-high pl-10 pr-4 text-sm text-on-surface placeholder:text-on-surface-variant/60 outline-none focus:ring-2 focus:ring-primary/30 transition"
          />
        </div>
      </div>

      {/* Right side: actions */}
      <div className="flex items-center gap-2">
        {/* Notification bell */}
        <button
          type="button"
          className="relative w-9 h-9 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition"
        >
          <span className="material-symbols-outlined text-xl">
            notifications
          </span>
        </button>

        {/* Language toggle */}
        <button
          type="button"
          onClick={toggleLanguage}
          className="h-9 rounded-lg px-3 text-sm font-medium text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition"
        >
          {i18n.language === 'fr' ? 'EN' : 'FR'}
        </button>

        {/* Divider */}
        <div className="w-px h-6 bg-surface-container-high mx-1" />

        {/* User name */}
        <span className="text-sm font-medium text-on-surface">
          {displayName}
        </span>

        {/* Logout */}
        <button
          type="button"
          onClick={logout}
          className="w-9 h-9 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high hover:text-error transition"
          title={t('auth.logout')}
        >
          <span className="material-symbols-outlined text-xl">
            logout
          </span>
        </button>
      </div>
    </header>
  );
}
