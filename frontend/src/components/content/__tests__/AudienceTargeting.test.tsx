import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AudienceTargeting } from '../AudienceTargeting';

describe('AudienceTargeting', () => {
  const defaultProps = {
    targetSites: [] as string[],
    targetDepartments: [] as string[],
    targetShifts: [] as string[],
    onSitesChange: vi.fn(),
    onDepartmentsChange: vi.fn(),
    onShiftsChange: vi.fn(),
    availableSites: [
      { id: 'site-1', name: 'Casablanca Nord' },
      { id: 'site-2', name: 'Casablanca Sud' },
    ],
  };

  it('renders all targeting sections', () => {
    render(<AudienceTargeting {...defaultProps} />);

    expect(screen.getByText('Ciblage audience')).toBeDefined();
    expect(screen.getByText('Sites')).toBeDefined();
    expect(screen.getByText('Départements')).toBeDefined();
    expect(screen.getByText('Équipes')).toBeDefined();
  });

  it('renders site selector with available sites', () => {
    render(<AudienceTargeting {...defaultProps} />);

    expect(screen.getByText('Sélectionner un site...')).toBeDefined();
    expect(screen.getByText('Casablanca Nord')).toBeDefined();
    expect(screen.getByText('Casablanca Sud')).toBeDefined();
  });

  it('renders selected sites as chips', () => {
    render(
      <AudienceTargeting
        {...defaultProps}
        targetSites={['site-1']}
      />,
    );

    expect(screen.getByText('Casablanca Nord')).toBeDefined();
  });

  it('adds department via chip input', () => {
    render(<AudienceTargeting {...defaultProps} />);

    const deptInput = screen.getByPlaceholderText('Ajouter un département...');
    fireEvent.change(deptInput, { target: { value: 'Marketing' } });
    fireEvent.keyDown(deptInput, { key: 'Enter' });

    expect(defaultProps.onDepartmentsChange).toHaveBeenCalledWith(['Marketing']);
  });

  it('renders selected departments as chips', () => {
    render(
      <AudienceTargeting
        {...defaultProps}
        targetDepartments={['IT', 'RH']}
      />,
    );

    expect(screen.getByText('IT')).toBeDefined();
    expect(screen.getByText('RH')).toBeDefined();
  });
});
