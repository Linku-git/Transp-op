import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import { useCallback, useEffect } from 'react';

interface RichTextEditorProps {
  value: string;
  onChange: (html: string) => void;
  placeholder?: string;
  error?: string;
}

function ToolbarButton({
  active,
  onClick,
  icon,
  title,
}: {
  active: boolean;
  onClick: () => void;
  icon: string;
  title: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      className={[
        'inline-flex items-center justify-center w-8 h-8 rounded-md text-sm transition-colors',
        active
          ? 'bg-primary/10 text-primary'
          : 'text-on-surface-variant hover:bg-surface-container-high/50',
      ].join(' ')}
    >
      <span className="material-symbols-outlined text-[18px]">{icon}</span>
    </button>
  );
}

export function RichTextEditor({
  value,
  onChange,
  placeholder = 'Saisissez le contenu...',
  error,
}: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder }),
    ],
    content: value,
    onUpdate: ({ editor: e }) => {
      onChange(e.getHTML());
    },
  });

  useEffect(() => {
    if (editor && value !== editor.getHTML()) {
      editor.commands.setContent(value, { emitUpdate: false });
    }
  }, [editor, value]);

  const toggleBold = useCallback(() => {
    editor?.chain().focus().toggleBold().run();
  }, [editor]);

  const toggleItalic = useCallback(() => {
    editor?.chain().focus().toggleItalic().run();
  }, [editor]);

  const toggleBulletList = useCallback(() => {
    editor?.chain().focus().toggleBulletList().run();
  }, [editor]);

  const toggleOrderedList = useCallback(() => {
    editor?.chain().focus().toggleOrderedList().run();
  }, [editor]);

  const toggleHeading = useCallback(() => {
    editor?.chain().focus().toggleHeading({ level: 3 }).run();
  }, [editor]);

  if (!editor) return null;

  return (
    <div>
      <div
        className={[
          'rounded-lg overflow-hidden transition-all',
          error
            ? 'ring-1 ring-error/40'
            : 'focus-within:ring-1 focus-within:ring-primary/20',
        ].join(' ')}
      >
        {/* Toolbar */}
        <div className="flex items-center gap-0.5 px-2 py-1.5 bg-surface-container-low/50 border-b border-outline-variant/10">
          <ToolbarButton
            active={editor.isActive('heading', { level: 3 })}
            onClick={toggleHeading}
            icon="title"
            title="Titre"
          />
          <ToolbarButton
            active={editor.isActive('bold')}
            onClick={toggleBold}
            icon="format_bold"
            title="Gras"
          />
          <ToolbarButton
            active={editor.isActive('italic')}
            onClick={toggleItalic}
            icon="format_italic"
            title="Italique"
          />
          <div className="w-px h-5 bg-outline-variant/15 mx-1" />
          <ToolbarButton
            active={editor.isActive('bulletList')}
            onClick={toggleBulletList}
            icon="format_list_bulleted"
            title="Liste"
          />
          <ToolbarButton
            active={editor.isActive('orderedList')}
            onClick={toggleOrderedList}
            icon="format_list_numbered"
            title="Liste numérotée"
          />
        </div>
        {/* Editor */}
        <EditorContent
          editor={editor}
          className="min-h-[200px] px-4 py-3 bg-surface-container-high/50 text-on-surface text-sm prose prose-sm max-w-none focus:outline-none [&_.tiptap]:outline-none [&_.tiptap]:min-h-[180px] [&_.is-editor-empty:first-child::before]:text-on-surface-variant/50 [&_.is-editor-empty:first-child::before]:content-[attr(data-placeholder)] [&_.is-editor-empty:first-child::before]:float-left [&_.is-editor-empty:first-child::before]:h-0 [&_.is-editor-empty:first-child::before]:pointer-events-none"
        />
      </div>
      {error && (
        <p className="mt-1 text-xs text-error">{error}</p>
      )}
    </div>
  );
}
