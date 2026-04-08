import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { language: 'fr' },
  }),
}));

vi.mock('@/stores/contentStore', () => ({
  useContentStore: () => ({
    createContent: vi.fn(),
  }),
}));

vi.mock('@/api/sites', () => ({
  listSites: vi.fn().mockResolvedValue({ data: [] }),
}));

vi.mock('@tiptap/react', () => ({
  useEditor: () => ({
    getHTML: () => '',
    commands: { setContent: vi.fn() },
    chain: () => ({ focus: () => ({ toggleBold: () => ({ run: vi.fn() }), toggleItalic: () => ({ run: vi.fn() }), toggleBulletList: () => ({ run: vi.fn() }), toggleOrderedList: () => ({ run: vi.fn() }), toggleHeading: () => ({ run: vi.fn() }) }) }),
    isActive: () => false,
  }),
  EditorContent: ({ children }: { children?: React.ReactNode }) => <div data-testid="editor-content">{children}</div>,
}));

vi.mock('@tiptap/starter-kit', () => ({ default: {} }));
vi.mock('@tiptap/extension-placeholder', () => ({
  default: { configure: () => ({}) },
}));

describe('ContentCreatePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders create form with all fields', async () => {
    const { ContentCreatePage } = await import('../ContentCreatePage');
    render(
      <MemoryRouter>
        <ContentCreatePage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Créer du contenu')).toBeDefined();
    expect(screen.getByPlaceholderText('Titre du contenu')).toBeDefined();
    expect(screen.getByText('Informations')).toBeDefined();
    expect(screen.getByText('Média')).toBeDefined();
    expect(screen.getByText('Planification')).toBeDefined();
  });

  it('renders content type selector with all options', async () => {
    const { ContentCreatePage } = await import('../ContentCreatePage');
    render(
      <MemoryRouter>
        <ContentCreatePage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Actualité')).toBeDefined();
    expect(screen.getByText('Formation')).toBeDefined();
    expect(screen.getByText('Sécurité')).toBeDefined();
    expect(screen.getByText('Sondage')).toBeDefined();
  });

  it('renders audience targeting section', async () => {
    const { ContentCreatePage } = await import('../ContentCreatePage');
    render(
      <MemoryRouter>
        <ContentCreatePage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Ciblage audience')).toBeDefined();
    expect(screen.getByText('Sites')).toBeDefined();
    expect(screen.getByText('Départements')).toBeDefined();
    expect(screen.getByText('Équipes')).toBeDefined();
  });

  it('renders preview button', async () => {
    const { ContentCreatePage } = await import('../ContentCreatePage');
    render(
      <MemoryRouter>
        <ContentCreatePage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Aperçu')).toBeDefined();
  });
});
