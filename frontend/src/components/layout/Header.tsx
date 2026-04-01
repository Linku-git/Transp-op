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
    <header className="bg-surface-container-lowest h-16 px-6 flex items-center justify-between">
      <div />

      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={toggleLanguage}
          className="rounded-md px-3 py-1.5 text-sm font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition"
        >
          {i18n.language === 'fr' ? 'EN' : 'FR'}
        </button>

        <span className="text-sm text-on-surface-variant">{displayName}</span>

        <button
          type="button"
          onClick={logout}
          className="rounded-md px-3 py-1.5 text-sm text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition"
        >
          {t('auth.logout')}
        </button>
      </div>
    </header>
  );
}
