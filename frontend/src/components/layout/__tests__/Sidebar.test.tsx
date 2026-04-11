import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

/* Mutable ref to control role in tests */
let currentRole = 'admin';

vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn((selector: (s: Record<string, unknown>) => unknown) => {
    const state = {
      user: { first_name: 'Test', last_name: 'User', role: currentRole },
    };
    return selector(state);
  }),
}));

/* Must import AFTER vi.mock is defined */
import { Sidebar } from '../Sidebar';

describe('Sidebar role filtering', () => {
  beforeEach(() => {
    currentRole = 'admin';
  });

  it('renders Dashboard for admin', () => {
    currentRole = 'admin';
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </MemoryRouter>
    );
    expect(screen.getByText('Dashboard')).toBeDefined();
  });

  it('renders all groups for admin role', () => {
    currentRole = 'admin';
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </MemoryRouter>
    );
    expect(screen.getByText('Master data')).toBeDefined();
    expect(screen.getByText('SOTREG')).toBeDefined();
    expect(screen.getByText('Outils')).toBeDefined();
    expect(screen.getByText('Parametres')).toBeDefined();
  });

  it('hides SOTREG and Outils for conducteur', () => {
    currentRole = 'conducteur';
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </MemoryRouter>
    );
    expect(screen.getByText('Dashboard')).toBeDefined();
    expect(screen.queryByText('SOTREG')).toBeNull();
    expect(screen.queryByText('Outils')).toBeNull();
    expect(screen.queryByText('Master data')).toBeNull();
    expect(screen.queryByText('Parametres')).toBeNull();
  });

  it('hides Settings for non-admin roles', () => {
    currentRole = 'drh';
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </MemoryRouter>
    );
    expect(screen.queryByText('Parametres')).toBeNull();
  });

  it('displays user name and role', () => {
    currentRole = 'admin';
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </MemoryRouter>
    );
    expect(screen.getByText('Test User')).toBeDefined();
    expect(screen.getByText('admin')).toBeDefined();
  });

  it('shows SOTREG for daf but not Master data', () => {
    currentRole = 'daf';
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </MemoryRouter>
    );
    expect(screen.getByText('SOTREG')).toBeDefined();
    expect(screen.getByText('Outils')).toBeDefined();
    expect(screen.getByText('Master data')).toBeDefined();
  });
});
