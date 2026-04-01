import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const t: Record<string, string> = {
        'sites.title': 'Sites',
        'sites.add': 'Ajouter un site',
        'sites.search': 'Rechercher...',
        'sites.columns.code': 'Code',
        'sites.columns.name': 'Nom',
        'sites.columns.city': 'Ville',
        'sites.columns.shifts': 'Equipes',
        'sites.columns.zfe': 'ZFE',
        'sites.columns.security': 'Securite',
        'sites.columns.actions': 'Actions',
        'sites.empty': 'Aucun site',
        'sites.filter_city': 'Filtrer par ville',
        'common.loading': 'Chargement...',
        'common.previous': 'Precedent',
        'common.next': 'Suivant',
      };
      return t[key] ?? key;
    },
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({
    sites: [
      { id: '1', code: 'S01', name: 'Site Alpha', city: 'Casablanca', num_shifts: 2, zfe_zone: true, security_profile: 'normal' },
      { id: '2', code: 'S02', name: 'Site Beta', city: 'Rabat', num_shifts: 1, zfe_zone: false, security_profile: 'elevated' },
    ],
    meta: { page: 1, pages: 1, total: 2, page_size: 20 },
    isLoading: false,
    error: null,
    fetchSites: vi.fn(),
    deleteSite: vi.fn(),
  }),
}));

describe('SiteListPage', () => {
  it('renders table with site data', async () => {
    const { SiteListPage } = await import('../SiteListPage');
    render(
      <MemoryRouter>
        <SiteListPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('nav.sites')).toBeInTheDocument();
    expect(screen.getByText('Site Alpha')).toBeInTheDocument();
    expect(screen.getByText('Site Beta')).toBeInTheDocument();
    expect(screen.getByText('Casablanca')).toBeInTheDocument();
  });
});
