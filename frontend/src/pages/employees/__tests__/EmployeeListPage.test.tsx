import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('@/stores/employeeStore', () => ({
  useEmployeeStore: () => ({
    employees: [
      { id: '1', matricule: 'EMP001', first_name: 'Alice', last_name: 'Dupont', site_name: 'Site Alpha', shift_time: 'Matin', is_pmr: true, current_transport_mode: 'Bus', opt_in_company_transport: 'Oui', active: true },
      { id: '2', matricule: 'EMP002', first_name: 'Bob', last_name: 'Martin', site_name: 'Site Beta', shift_time: 'Nuit', is_pmr: false, current_transport_mode: 'Voiture', opt_in_company_transport: 'Non', active: true },
    ],
    meta: { page: 1, pages: 1, total: 2, page_size: 20 },
    isLoading: false,
    error: null,
    fetchEmployees: vi.fn(),
    deleteEmployee: vi.fn(),
  }),
}));

vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({
    sites: [{ id: 's1', code: 'S01', name: 'Site Alpha' }],
    fetchSites: vi.fn(),
  }),
}));

describe('EmployeeListPage', () => {
  it('renders table with employee data', async () => {
    const { EmployeeListPage } = await import('../EmployeeListPage');
    render(
      <MemoryRouter>
        <EmployeeListPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Alice Dupont')).toBeInTheDocument();
    expect(screen.getByText('Bob Martin')).toBeInTheDocument();
    expect(screen.getByText('EMP001')).toBeInTheDocument();
  });
});
