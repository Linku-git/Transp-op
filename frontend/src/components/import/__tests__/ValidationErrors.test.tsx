import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

describe('ValidationErrors', () => {
  it('displays errors with row references', async () => {
    const { ValidationErrors } = await import('../ValidationErrors');
    render(
      <ValidationErrors
        errors={[
          { sheet: 'SITES', row: 3, column: 'Code Site', message: 'Required field' },
          { sheet: 'SITES', row: 5, column: 'Latitude', message: 'Invalid value' },
        ]}
      />,
    );

    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Required field')).toBeInTheDocument();
    expect(screen.getByText('Invalid value')).toBeInTheDocument();
  });

  it('shows success when no errors', async () => {
    const { ValidationErrors } = await import('../ValidationErrors');
    render(<ValidationErrors errors={[]} />);

    expect(screen.getByText(/erreur/i)).toBeInTheDocument();
  });
});
