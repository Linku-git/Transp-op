import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Button } from '../Button'

describe('Button', () => {
  it('renders all variants', () => {
    const variants = ['primary', 'secondary', 'danger', 'ghost'] as const

    for (const variant of variants) {
      const { unmount } = render(
        <Button variant={variant}>{variant}</Button>
      )
      expect(screen.getByRole('button', { name: variant })).toBeInTheDocument()
      unmount()
    }
  })

  it('shows spinner when loading', () => {
    render(<Button isLoading>Loading</Button>)
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button.querySelector('svg')).toBeInTheDocument()
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
