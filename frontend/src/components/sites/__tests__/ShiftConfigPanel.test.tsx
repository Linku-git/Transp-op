import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ShiftConfigPanel } from '../ShiftConfigPanel';
import type { Site } from '@/types/site';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const baseSite: Site = {
  id: '1',
  tenant_id: 't1',
  code: 'S01',
  name: 'Test',
  address: 'Addr',
  city: 'City',
  lat: 0,
  lng: 0,
  num_shifts: 2,
  shift_1_entry: '08:00',
  shift_1_exit: '16:00',
  shift_2_entry: '16:00',
  shift_2_exit: '00:00',
  shift_3_entry: null,
  shift_3_exit: null,
  working_days: 'Lundi-Vendredi',
  days_per_week: 5,
  contact_name: null,
  contact_phone: null,
  access_notes: null,
  parking_notes: null,
  zfe_zone: false,
  security_profile: 'normal',
  timezone: 'Europe/Paris',
  observations: null,
  created_at: '',
  updated_at: '',
};

describe('ShiftConfigPanel', () => {
  it('renders shift bars with correct times', () => {
    render(<ShiftConfigPanel site={baseSite} />);

    expect(screen.getByText('Horaires')).toBeInTheDocument();
    expect(screen.getByText(/08:00/)).toBeInTheDocument();
    expect(screen.getAllByText(/16:00/).length).toBeGreaterThan(0);
  });

  it('shows 2 shift rows for num_shifts=2', () => {
    render(<ShiftConfigPanel site={baseSite} />);

    const shiftLabels = screen.getAllByText(/Equipe/);
    expect(shiftLabels.length).toBe(2);
  });
});
