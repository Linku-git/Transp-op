import { useTranslation } from 'react-i18next';

export function LoginPage() {
  const { t } = useTranslation();

  return (
    <div className="bg-surface min-h-screen flex items-center justify-center">
      <div className="bg-surface-container-lowest rounded-lg shadow-md p-8 w-full max-w-md">
        <h1 className="font-display text-3xl font-bold text-primary text-center mb-8">
          {t('app.name')}
        </h1>

        <form
          onSubmit={(e) => {
            e.preventDefault();
          }}
          className="flex flex-col gap-5"
        >
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="email"
              className="text-sm font-medium text-on-surface-variant"
            >
              {t('auth.email')}
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              className="bg-surface-container-high rounded-md px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-secondary/40 transition"
              placeholder="nom@entreprise.fr"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="password"
              className="text-sm font-medium text-on-surface-variant"
            >
              {t('auth.password')}
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className="bg-surface-container-high rounded-md px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-secondary/40 transition"
            />
          </div>

          <button
            type="submit"
            className="bg-secondary text-on-secondary rounded-md px-4 py-2.5 text-sm font-medium hover:opacity-90 transition mt-2"
          >
            {t('auth.login')}
          </button>
        </form>
      </div>
    </div>
  );
}
