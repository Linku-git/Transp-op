import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '@/api/client';
import { useAuthStore } from '@/stores/authStore';

export function LoginPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [emailFocused, setEmailFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);

  const currentLang = i18n.language?.startsWith('fr') ? 'fr' : 'en';

  const toggleLanguage = () => {
    const next = currentLang === 'fr' ? 'en' : 'fr';
    i18n.changeLanguage(next);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const resp = await api.post('/api/v1/auth/login', { email, password });
      const { access_token } = resp.data;

      const meResp = await api.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      login(access_token, meResp.data);
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? t('auth.loginError', 'Email ou mot de passe incorrect');
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-surface flex items-center justify-center overflow-hidden px-4">
      {/* Abstract background circles */}
      <div
        className="pointer-events-none absolute -top-32 -right-32 h-[480px] w-[480px] rounded-full bg-primary/5"
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute -bottom-40 -left-40 h-[560px] w-[560px] rounded-full bg-secondary/5"
        aria-hidden="true"
      />

      <div className="relative z-10 w-full max-w-md flex flex-col items-center gap-8">
        {/* Logo and branding */}
        <div className="flex flex-col items-center gap-2 select-none">
          <div className="flex items-center gap-3">
            <span
              className="material-symbols-outlined text-primary"
              style={{ fontSize: '36px' }}
            >
              directions_bus
            </span>
            <span className="font-headline text-2xl font-bold tracking-tight text-on-surface">
              {t('app.name')} Mobility
            </span>
          </div>
          <span className="font-sans text-sm font-medium tracking-widest uppercase text-on-surface-variant">
            {t('auth.subtitle', 'Mobility Admin')}
          </span>
        </div>

        {/* Login card */}
        <div className="w-full bg-surface-container-lowest rounded-xl p-8 shadow-md">
          {/* Error banner */}
          {error && (
            <div className="mb-6 flex items-center gap-2 rounded-lg bg-error-container px-4 py-3 text-sm text-on-error-container">
              <span className="material-symbols-outlined text-error" style={{ fontSize: '20px' }}>
                error
              </span>
              {error}
            </div>
          )}

          {/* SSO button */}
          <button
            type="button"
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-primary to-primary-container px-4 py-3 text-sm font-semibold text-on-primary transition-opacity hover:opacity-90 active:opacity-80"
          >
            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
              key
            </span>
            {t('auth.sso', 'Enterprise SSO Login')}
          </button>

          {/* Divider */}
          <div className="my-6 flex items-center gap-4">
            <div className="h-px flex-1 bg-surface-container-high" />
            <span className="font-sans text-xs font-medium tracking-wider text-on-surface-variant whitespace-nowrap">
              {t('auth.or_continue', 'OR CONTINUE WITH EMAIL')}
            </span>
            <div className="h-px flex-1 bg-surface-container-high" />
          </div>

          {/* Email/password form */}
          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            {/* Email field */}
            <div className="relative">
              <input
                id="login-email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => setEmailFocused(true)}
                onBlur={() => setEmailFocused(false)}
                required
                placeholder=" "
                className="peer w-full rounded-lg bg-surface-container-high border-none px-4 pt-5 pb-2 text-sm text-on-surface placeholder-transparent outline-none transition-all focus:ring-0"
              />
              <label
                htmlFor="login-email"
                className={[
                  'pointer-events-none absolute left-4 transition-all duration-200 font-sans',
                  email || emailFocused
                    ? 'top-1.5 text-xs font-medium text-primary'
                    : 'top-3.5 text-sm text-on-surface-variant',
                ].join(' ')}
              >
                {t('auth.email')}
              </label>
              {/* Focus underline */}
              <div
                className={[
                  'absolute bottom-0 left-1/2 h-0.5 bg-primary rounded-full transition-all duration-300',
                  emailFocused ? 'w-full -translate-x-1/2' : 'w-0 -translate-x-1/2',
                ].join(' ')}
              />
            </div>

            {/* Password field */}
            <div className="relative">
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => setPasswordFocused(true)}
                onBlur={() => setPasswordFocused(false)}
                required
                placeholder=" "
                className="peer w-full rounded-lg bg-surface-container-high border-none px-4 pt-5 pb-2 text-sm text-on-surface placeholder-transparent outline-none transition-all focus:ring-0"
              />
              <label
                htmlFor="login-password"
                className={[
                  'pointer-events-none absolute left-4 transition-all duration-200 font-sans',
                  password || passwordFocused
                    ? 'top-1.5 text-xs font-medium text-primary'
                    : 'top-3.5 text-sm text-on-surface-variant',
                ].join(' ')}
              >
                {t('auth.password')}
              </label>
              <div
                className={[
                  'absolute bottom-0 left-1/2 h-0.5 bg-primary rounded-full transition-all duration-300',
                  passwordFocused ? 'w-full -translate-x-1/2' : 'w-0 -translate-x-1/2',
                ].join(' ')}
              />
            </div>

            {/* Remember me + Forgot password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="h-4 w-4 rounded accent-primary"
                />
                <span className="text-xs text-on-surface-variant font-sans">
                  {t('auth.remember_me', 'Remember me')}
                </span>
              </label>
              <button
                type="button"
                className="text-xs font-medium text-primary hover:underline font-sans"
              >
                {t('auth.forgot_password', 'Forgot password?')}
              </button>
            </div>

            {/* Sign In button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-surface-container-high px-4 py-3 text-sm font-semibold text-on-surface-variant transition-colors hover:bg-surface-container-highest active:bg-surface-container disabled:opacity-50"
            >
              {isLoading
                ? t('common.loading', 'Chargement...')
                : t('auth.login')}
            </button>
          </form>
        </div>

        {/* Language selector pill */}
        <button
          type="button"
          onClick={toggleLanguage}
          className="flex items-center gap-2 rounded-full bg-surface-container-lowest px-4 py-2 shadow-sm transition-colors hover:bg-surface-container-low"
        >
          <span className="material-symbols-outlined text-on-surface-variant" style={{ fontSize: '18px' }}>
            language
          </span>
          <span className="text-xs font-medium text-on-surface-variant uppercase tracking-wider font-sans">
            {currentLang === 'fr' ? 'EN' : 'FR'}
          </span>
        </button>

        {/* Footer links */}
        <div className="flex items-center gap-4 text-xs text-on-surface-variant font-sans">
          <button type="button" className="hover:text-on-surface transition-colors hover:underline">
            {t('auth.privacy_policy', 'Privacy Policy')}
          </button>
          <span className="text-surface-container-high" aria-hidden="true">|</span>
          <button type="button" className="hover:text-on-surface transition-colors hover:underline">
            {t('auth.terms', 'Terms')}
          </button>
          <span className="text-surface-container-high" aria-hidden="true">|</span>
          <button type="button" className="hover:text-on-surface transition-colors hover:underline">
            {t('auth.support', 'Support')}
          </button>
        </div>
      </div>
    </div>
  );
}
