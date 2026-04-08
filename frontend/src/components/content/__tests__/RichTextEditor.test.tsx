import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@tiptap/react', () => ({
  useEditor: () => ({
    getHTML: () => '<p>test</p>',
    commands: { setContent: vi.fn() },
    chain: () => ({
      focus: () => ({
        toggleBold: () => ({ run: vi.fn() }),
        toggleItalic: () => ({ run: vi.fn() }),
        toggleBulletList: () => ({ run: vi.fn() }),
        toggleOrderedList: () => ({ run: vi.fn() }),
        toggleHeading: () => ({ run: vi.fn() }),
      }),
    }),
    isActive: () => false,
  }),
  EditorContent: () => <div data-testid="editor-content" />,
}));

vi.mock('@tiptap/starter-kit', () => ({ default: {} }));
vi.mock('@tiptap/extension-placeholder', () => ({
  default: { configure: () => ({}) },
}));

describe('RichTextEditor', () => {
  it('renders toolbar with formatting buttons', async () => {
    const { RichTextEditor } = await import('../RichTextEditor');
    render(
      <RichTextEditor value="" onChange={vi.fn()} />,
    );

    expect(screen.getByTitle('Gras')).toBeDefined();
    expect(screen.getByTitle('Italique')).toBeDefined();
    expect(screen.getByTitle('Liste')).toBeDefined();
    expect(screen.getByTitle('Liste numérotée')).toBeDefined();
    expect(screen.getByTitle('Titre')).toBeDefined();
  });

  it('renders editor content area', async () => {
    const { RichTextEditor } = await import('../RichTextEditor');
    render(
      <RichTextEditor value="" onChange={vi.fn()} />,
    );

    expect(screen.getByTestId('editor-content')).toBeDefined();
  });

  it('shows error message when provided', async () => {
    const { RichTextEditor } = await import('../RichTextEditor');
    render(
      <RichTextEditor value="" onChange={vi.fn()} error="Champ requis" />,
    );

    expect(screen.getByText('Champ requis')).toBeDefined();
  });
});
