import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

describe('SheetPreview', () => {
  it('renders data table with columns', async () => {
    const { SheetPreview } = await import('../SheetPreview');
    render(
      <SheetPreview
        data={[
          { Name: 'Alice', City: 'Paris' },
          { Name: 'Bob', City: 'Lyon' },
        ]}
      />,
    );

    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Lyon')).toBeInTheDocument();
  });
});
