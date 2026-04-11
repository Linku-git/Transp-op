import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

describe('RoleManagementPage', () => {
  it('renders all 9 roles', async () => {
    const mod = await import('../RoleManagementPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>
    );
    expect(screen.getByText('Administrateur')).toBeDefined();
    expect(screen.getByText('DRH')).toBeDefined();
    expect(screen.getByText('DAF')).toBeDefined();
    expect(screen.getByText('Responsable Parc')).toBeDefined();
    expect(screen.getByText('Resp. Exploitation')).toBeDefined();
    expect(screen.getByText('Prestataire')).toBeDefined();
    expect(screen.getByText('Conducteur')).toBeDefined();
    expect(screen.getAllByText('Salarie').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Operateur').length).toBeGreaterThanOrEqual(1);
  });

  it('renders page header', async () => {
    const mod = await import('../RoleManagementPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>
    );
    expect(screen.getByText('Gestion des Roles')).toBeDefined();
  });

  it('renders hierarchy info banner', async () => {
    const mod = await import('../RoleManagementPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>
    );
    expect(screen.getByText('Hierarchie des roles')).toBeDefined();
    expect(screen.getByText('Administration')).toBeDefined();
    expect(screen.getByText('Direction')).toBeDefined();
    expect(screen.getByText('Management')).toBeDefined();
  });

  it('shows module badges for admin role', async () => {
    const mod = await import('../RoleManagementPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>
    );
    expect(screen.getByText('M1-M8')).toBeDefined();
    expect(screen.getAllByText('Admin').length).toBeGreaterThanOrEqual(1);
  });

  it('displays search input', async () => {
    const mod = await import('../RoleManagementPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>
    );
    expect(screen.getByPlaceholderText('Rechercher un role...')).toBeDefined();
  });
});
