import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatWidget } from '../ChatWidget';

// Mock fetch for Rasa API
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: vi.fn((index: number) => Object.keys(store)[index] ?? null),
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock scrollIntoView
Element.prototype.scrollIntoView = vi.fn();

describe('ChatWidget', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.clear();
    mockFetch.mockReset();
  });

  it('renders floating chat button', () => {
    render(<ChatWidget />);
    const fab = screen.getByTestId('chat-fab');
    expect(fab).toBeInTheDocument();
    expect(fab).toHaveAttribute('aria-label', 'Ouvrir le chat');
  });

  it('opens chat panel on button click', () => {
    render(<ChatWidget />);
    expect(screen.queryByTestId('chat-panel')).not.toBeInTheDocument();

    fireEvent.click(screen.getByTestId('chat-fab'));

    expect(screen.getByTestId('chat-panel')).toBeInTheDocument();
    expect(screen.getByText('Assistant Transpop')).toBeInTheDocument();
  });

  it('sends message and displays in chat', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ recipient_id: 'test', text: 'Bot reply' }],
    });

    render(<ChatWidget />);
    fireEvent.click(screen.getByTestId('chat-fab'));

    const input = screen.getByTestId('chat-input');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByTestId('chat-send-btn'));

    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('displays bot response after sending', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ recipient_id: 'test', text: 'Voici votre reponse' }],
    });

    render(<ChatWidget />);
    fireEvent.click(screen.getByTestId('chat-fab'));

    const input = screen.getByTestId('chat-input');
    fireEvent.change(input, { target: { value: 'Bonjour' } });
    fireEvent.click(screen.getByTestId('chat-send-btn'));

    await waitFor(() => {
      expect(screen.getByText('Voici votre reponse')).toBeInTheDocument();
    });
  });

  it('shows typing indicator while waiting', async () => {
    // Create a promise we control to keep fetch pending
    let resolvePromise: (value: Response) => void;
    const pendingPromise = new Promise<Response>((resolve) => {
      resolvePromise = resolve;
    });
    mockFetch.mockReturnValueOnce(pendingPromise);

    render(<ChatWidget />);
    fireEvent.click(screen.getByTestId('chat-fab'));

    const input = screen.getByTestId('chat-input');
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(screen.getByTestId('chat-send-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
    });

    // Resolve the pending fetch
    resolvePromise!({
      ok: true,
      json: async () => [{ recipient_id: 'test', text: 'Done' }],
    } as Response);

    await waitFor(() => {
      expect(screen.queryByTestId('typing-indicator')).not.toBeInTheDocument();
    });
  });

  it('persists messages in localStorage', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ recipient_id: 'test', text: 'Saved reply' }],
    });

    render(<ChatWidget />);
    fireEvent.click(screen.getByTestId('chat-fab'));

    const input = screen.getByTestId('chat-input');
    fireEvent.change(input, { target: { value: 'Persist me' } });
    fireEvent.click(screen.getByTestId('chat-send-btn'));

    await waitFor(() => {
      expect(screen.getByText('Saved reply')).toBeInTheDocument();
    });

    // Verify localStorage was called with our messages
    const calls = localStorageMock.setItem.mock.calls.filter(
      (c: string[]) => c[0] === 'transpop-chat-history',
    );
    expect(calls.length).toBeGreaterThan(0);

    const lastCall = calls[calls.length - 1];
    const saved = JSON.parse(lastCall[1] as string) as Array<{ text: string }>;
    const texts = saved.map((m) => m.text);
    expect(texts).toContain('Persist me');
    expect(texts).toContain('Saved reply');
  });

  it('loads saved messages from localStorage', () => {
    const savedMessages = [
      {
        id: 'saved-1',
        text: 'Previously saved message',
        sender: 'user',
        timestamp: new Date().toISOString(),
      },
      {
        id: 'saved-2',
        text: 'Bot saved reply',
        sender: 'bot',
        timestamp: new Date().toISOString(),
      },
    ];
    localStorageMock.setItem('transpop-chat-history', JSON.stringify(savedMessages));

    render(<ChatWidget />);
    fireEvent.click(screen.getByTestId('chat-fab'));

    expect(screen.getByText('Previously saved message')).toBeInTheDocument();
    expect(screen.getByText('Bot saved reply')).toBeInTheDocument();
  });

  it('closes chat panel on close button click', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByTestId('chat-fab'));
    expect(screen.getByTestId('chat-panel')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('chat-close-btn'));
    expect(screen.queryByTestId('chat-panel')).not.toBeInTheDocument();
  });
});
