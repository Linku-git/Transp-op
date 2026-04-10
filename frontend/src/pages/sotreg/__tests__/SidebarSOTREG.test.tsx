import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';

vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    user: { first_name: 'Ayoub', last_name: 'Test', role: 'admin' },
  }),
}));

describe('Sidebar SOTREG section', () => {
  it('shows SOTREG navigation group in expanded sidebar', () => {
    render(
      <MemoryRouter>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </MemoryRouter>,
    );

    expect(screen.getByText('SOTREG')).toBeDefined();
  });

  it('shows SOTREG sub-items when group is expanded', () => {
    render(
      <MemoryRouter initialEntries={['/sotreg']}>
        <Sidebar collapsed={false} onToggle={() => {}} />
      </MemoryRouter>,
    );

    // When navigated to /sotreg, the group should auto-expand
    expect(screen.getByText('Diagnostic Flotte')).toBeDefined();
    expect(screen.getByText('Lignes Transport')).toBeDefined();
  });
});
