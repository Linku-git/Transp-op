import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('@/api/import', () => ({
  previewExcel: vi.fn(),
  importExcel: vi.fn(),
  importSheet: vi.fn(),
}));

describe('ExcelImportPage', () => {
  it('renders upload area', async () => {
    const { ExcelImportPage } = await import('../ExcelImportPage');
    render(
      <MemoryRouter>
        <ExcelImportPage />
      </MemoryRouter>,
    );

    expect(screen.getAllByText(/Import/i).length).toBeGreaterThan(0);
  });
});
