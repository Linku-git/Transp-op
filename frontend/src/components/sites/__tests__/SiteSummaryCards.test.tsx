import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SiteSummaryCards } from '../SiteSummaryCards';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

describe('SiteSummaryCards', () => {
  it('renders correct counts', () => {
    render(
      <SiteSummaryCards
        summary={{ employee_count: 42, vehicle_count: 5, pmr_count: 3 }}
      />,
    );

    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('Employes')).toBeInTheDocument();
    expect(screen.getByText('Vehicules')).toBeInTheDocument();
    expect(screen.getByText('PMR')).toBeInTheDocument();
  });
});
