import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Card } from '../Card'

describe('Card', () => {
  it('renders title and content', () => {
    render(
      <Card title="Test Title">
        <p>Card content</p>
      </Card>
    )
    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders without title', () => {
    render(
      <Card>
        <p>Just content</p>
      </Card>
    )
    expect(screen.getByText('Just content')).toBeInTheDocument()
    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
  })
})
