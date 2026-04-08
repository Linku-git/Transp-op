import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { language: 'fr' },
  }),
}));

const mockFetchContents = vi.fn();
const mockDeleteContent = vi.fn();
const mockPublishContent = vi.fn();

vi.mock('@/stores/contentStore', () => ({
  useContentStore: () => ({
    contents: [
      {
        id: '1',
        tenant_id: 't1',
        title: 'Bienvenue chez Transpop',
        body: '<p>Contenu test</p>',
        content_type: 'news' as const,
        media_url: null,
        target_sites: ['site-1'],
        target_departments: ['IT'],
        target_shifts: [],
        published_at: '2026-04-08T10:00:00Z',
        expires_at: null,
        created_by: 'u1',
        is_active: true,
        created_at: '2026-04-08T09:00:00Z',
        updated_at: '2026-04-08T10:00:00Z',
      },
      {
        id: '2',
        tenant_id: 't1',
        title: 'Formation sécurité',
        body: '<p>Formation</p>',
        content_type: 'training' as const,
        media_url: null,
        target_sites: [],
        target_departments: [],
        target_shifts: [],
        published_at: null,
        expires_at: null,
        created_by: 'u1',
        is_active: true,
        created_at: '2026-04-08T09:00:00Z',
        updated_at: '2026-04-08T09:00:00Z',
      },
    ],
    meta: { page: 1, pages: 1, total: 2 },
    isLoading: false,
    error: null,
    fetchContents: mockFetchContents,
    deleteContent: mockDeleteContent,
    publishContent: mockPublishContent,
  }),
}));

describe('ContentListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders content table with items', async () => {
    const { ContentListPage } = await import('../ContentListPage');
    render(
      <MemoryRouter>
        <ContentListPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Bienvenue chez Transpop')).toBeDefined();
    expect(screen.getByText('Formation sécurité')).toBeDefined();
  });

  it('shows content type labels', async () => {
    const { ContentListPage } = await import('../ContentListPage');
    render(
      <MemoryRouter>
        <ContentListPage />
      </MemoryRouter>,
    );

    expect(screen.getAllByText('Actualité').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Formation').length).toBeGreaterThanOrEqual(1);
  });

  it('renders filter controls', async () => {
    const { ContentListPage } = await import('../ContentListPage');
    render(
      <MemoryRouter>
        <ContentListPage />
      </MemoryRouter>,
    );

    expect(screen.getByPlaceholderText('Rechercher par titre...')).toBeDefined();
    expect(screen.getByText('Tous les types')).toBeDefined();
    expect(screen.getByText('Tous les statuts')).toBeDefined();
  });

  it('shows status badges', async () => {
    const { ContentListPage } = await import('../ContentListPage');
    render(
      <MemoryRouter>
        <ContentListPage />
      </MemoryRouter>,
    );

    expect(screen.getAllByText('Publié').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Brouillon').length).toBeGreaterThanOrEqual(1);
  });

  it('calls fetchContents on mount', async () => {
    const { ContentListPage } = await import('../ContentListPage');
    render(
      <MemoryRouter>
        <ContentListPage />
      </MemoryRouter>,
    );

    expect(mockFetchContents).toHaveBeenCalled();
  });
});
