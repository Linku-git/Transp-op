interface ChatMessageProps {
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export function ChatMessage({ text, sender, timestamp }: ChatMessageProps) {
  const isUser = sender === 'user';

  const formattedTime = timestamp.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div
      className={[
        'flex flex-col max-w-[80%]',
        isUser ? 'ml-auto items-end' : 'mr-auto items-start',
      ].join(' ')}
    >
      <div
        className={[
          'px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap break-words',
          isUser
            ? 'bg-primary text-on-primary rounded-2xl rounded-br-md'
            : 'bg-surface-container rounded-2xl rounded-bl-md text-on-surface',
        ].join(' ')}
      >
        {!isUser && (
          <span className="material-symbols-outlined text-primary mr-1.5 text-base align-middle">
            smart_toy
          </span>
        )}
        {text}
      </div>
      <span className="text-[10px] text-on-surface-variant mt-1 px-1">
        {formattedTime}
      </span>
    </div>
  );
}
