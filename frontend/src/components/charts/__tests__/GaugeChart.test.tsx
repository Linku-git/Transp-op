import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

describe('GaugeChart', () => {
  it('renders an SVG element with role="img"', async () => {
    const { GaugeChart } = await import('../GaugeChart');
    render(<GaugeChart value={75} />);

    const svg = screen.getByRole('img');
    expect(svg).toBeInTheDocument();
    expect(svg.tagName.toLowerCase()).toBe('svg');
  });

  it('displays the value as a percentage text', async () => {
    const { GaugeChart } = await import('../GaugeChart');
    render(<GaugeChart value={75} />);

    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('clamps value to 0-100 range', async () => {
    const { GaugeChart } = await import('../GaugeChart');
    const { rerender } = render(<GaugeChart value={150} />);

    // 150 is clamped to 100
    expect(screen.getByText('100%')).toBeInTheDocument();

    rerender(<GaugeChart value={-20} />);
    // -20 is clamped to 0
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('renders label when provided', async () => {
    const { GaugeChart } = await import('../GaugeChart');
    render(<GaugeChart value={60} label="Occupancy" />);

    expect(screen.getByText('Occupancy')).toBeInTheDocument();
  });

  it('does not render label when omitted', async () => {
    const { GaugeChart } = await import('../GaugeChart');
    render(<GaugeChart value={60} />);

    // No extra text element beyond the percentage
    expect(screen.queryByText('Occupancy')).not.toBeInTheDocument();
  });

  it('includes accessible aria-label with value', async () => {
    const { GaugeChart } = await import('../GaugeChart');
    render(<GaugeChart value={42} label="Rate" />);

    const svg = screen.getByRole('img');
    expect(svg).toHaveAttribute('aria-label', '42% Rate');
  });

  it('renders two path elements (background arc and value arc)', async () => {
    const { GaugeChart } = await import('../GaugeChart');
    const { container } = render(<GaugeChart value={50} />);

    const paths = container.querySelectorAll('path');
    expect(paths.length).toBe(2);
  });

  it('respects custom size prop', async () => {
    const { GaugeChart } = await import('../GaugeChart');
    render(<GaugeChart value={50} size={200} />);

    const svg = screen.getByRole('img');
    expect(svg).toHaveAttribute('width', '200');
  });
});
