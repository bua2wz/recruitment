import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

// Mock fetch
global.fetch = vi.fn()

beforeEach(() => {
  vi.resetAllMocks()
  ;(global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
    json: async () => []
  })
})

describe('App', () => {
  it('renders the app title', async () => {
    render(<App />)
    expect(screen.getByText('Blog Post Manager')).toBeDefined()
  })

  it('renders tabs for navigation', async () => {
    render(<App />)
    expect(screen.getByText('All Posts')).toBeDefined()
    expect(screen.getByText('Search')).toBeDefined()
    expect(screen.getByText('Generate')).toBeDefined()
  })

  it('renders new post button', async () => {
    render(<App />)
    expect(screen.getByText('New Post')).toBeDefined()
  })

  it('fetches posts on mount', async () => {
    render(<App />)
    expect(global.fetch).toHaveBeenCalledWith('/api/posts')
  })
})
