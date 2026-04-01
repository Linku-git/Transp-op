import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Badge } from '../Badge';

describe('Badge', () => {
  it('renders all variants', () => {
    const variants = ['success', 'warning', 'danger', 'info', 'neutral'] as const;

    for (const variant of variants) {
      const { unmount } = render(<Badge variant={variant}>{variant}</Badge>);
      expect(screen.getByText(variant)).toBeInTheDocument();
      unmount();
    }
  });

  it('applies custom className', () => {
    render(<Badge variant="success" className="ml-2">Test</Badge>);
    const badge = screen.getByText('Test');
    expect(badge.className).toContain('ml-2');
  });
});
