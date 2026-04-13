import { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage } from './ChatMessage';

const RASA_URL = import.meta.env.VITE_RASA_URL || 'http://localhost:5005';
const STORAGE_KEY = 'transpop-chat-history';
const SENDER_ID = 'transpop-web-user';

const GREETING_MESSAGE: Message = {
  id: 'greeting-0',
  text: 'Bonjour ! Je suis l\'assistant Transpop. Comment puis-je vous aider ?',
  sender: 'bot',
  timestamp: new Date().toISOString(),
};

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

interface RasaResponse {
  recipient_id: string;
  text?: string;
  image?: string;
  buttons?: Array<{ title: string; payload: string }>;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function loadMessages(): Message[] {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed: unknown = JSON.parse(saved);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed as Message[];
      }
    }
  } catch {
    // Corrupted storage — start fresh
  }
  return [];
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 mr-auto max-w-[80%]" data-testid="typing-indicator">
      <div className="bg-surface-container rounded-2xl rounded-bl-md px-4 py-3 flex items-center gap-1.5">
        <span className="material-symbols-outlined text-primary mr-1 text-base">
          smart_toy
        </span>
        <span className="w-2 h-2 rounded-full bg-on-surface-variant/40 animate-bounce [animation-delay:0ms]" />
        <span className="w-2 h-2 rounded-full bg-on-surface-variant/40 animate-bounce [animation-delay:150ms]" />
        <span className="w-2 h-2 rounded-full bg-on-surface-variant/40 animate-bounce [animation-delay:300ms]" />
      </div>
    </div>
  );
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(loadMessages);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [hasGreeted, setHasGreeted] = useState(() => {
    return loadMessages().length > 0;
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Persist messages to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setUnreadCount(0);
    }
  }, [isOpen]);

  // Send greeting on first open
  useEffect(() => {
    if (isOpen && !hasGreeted) {
      setMessages([GREETING_MESSAGE]);
      setHasGreeted(true);
    }
  }, [isOpen, hasGreeted]);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    const userMessage: Message = {
      id: generateId(),
      text: trimmed,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch(`${RASA_URL}/webhooks/rest/webhook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender: SENDER_ID, message: trimmed }),
      });

      if (!response.ok) {
        throw new Error(`Rasa returned ${response.status}`);
      }

      const data: RasaResponse[] = await response.json();

      const botMessages: Message[] = data
        .filter((r) => r.text)
        .map((r) => ({
          id: generateId(),
          text: r.text as string,
          sender: 'bot' as const,
          timestamp: new Date().toISOString(),
        }));

      if (botMessages.length === 0) {
        botMessages.push({
          id: generateId(),
          text: 'Hmm, je n\'ai pas de reponse pour le moment. Pouvez-vous reformuler ?',
          sender: 'bot',
          timestamp: new Date().toISOString(),
        });
      }

      setMessages((prev) => [...prev, ...botMessages]);

      if (!isOpen) {
        setUnreadCount((c) => c + botMessages.length);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          text: 'Desolee, je ne peux pas me connecter au serveur. Veuillez reessayer plus tard.',
          sender: 'bot',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }, [isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const clearHistory = () => {
    setMessages([]);
    setHasGreeted(false);
    localStorage.removeItem(STORAGE_KEY);
  };

  const toggleOpen = () => {
    setIsOpen((prev) => !prev);
  };

  const canSend = input.trim().length > 0 && !isTyping;

  return (
    <>
      {/* Chat Panel */}
      {isOpen && (
        <div
          className="fixed bottom-24 right-6 w-96 h-[32rem] rounded-2xl bg-surface-container-lowest shadow-2xl border border-outline-variant/10 z-50 flex flex-col overflow-hidden"
          data-testid="chat-panel"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-primary to-primary-container text-on-primary rounded-t-2xl p-4 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-xl">
                smart_toy
              </span>
              <span className="font-sans font-semibold text-sm">
                Assistant Transpop
              </span>
            </div>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={clearHistory}
                className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/20 transition"
                title="Effacer l'historique"
              >
                <span className="material-symbols-outlined text-lg">
                  delete
                </span>
              </button>
              <button
                type="button"
                onClick={toggleOpen}
                className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/20 transition"
                title="Fermer"
                data-testid="chat-close-btn"
              >
                <span className="material-symbols-outlined text-lg">
                  close
                </span>
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-on-surface-variant/60">
                <span className="material-symbols-outlined text-4xl mb-2">
                  forum
                </span>
                <p className="text-sm">Commencez une conversation</p>
              </div>
            )}
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                text={msg.text}
                sender={msg.sender}
                timestamp={new Date(msg.timestamp)}
              />
            ))}
            {isTyping && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-outline-variant/10 p-3 flex gap-2 shrink-0">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Tapez votre message..."
              className="bg-surface-container-high/50 border-none rounded-full px-4 py-2 flex-1 text-sm text-on-surface placeholder:text-on-surface-variant/50 outline-none focus:ring-2 focus:ring-primary/20 transition"
              data-testid="chat-input"
            />
            <button
              type="button"
              onClick={() => sendMessage(input)}
              disabled={!canSend}
              className={[
                'w-10 h-10 rounded-full flex items-center justify-center transition-all duration-150 shrink-0',
                canSend
                  ? 'bg-primary text-on-primary shadow-md shadow-primary/20 hover:scale-105 active:scale-95 cursor-pointer'
                  : 'bg-surface-container-high text-on-surface-variant/40 cursor-not-allowed',
              ].join(' ')}
              data-testid="chat-send-btn"
            >
              <span className="material-symbols-outlined text-lg">
                send
              </span>
            </button>
          </div>
        </div>
      )}

      {/* Floating Action Button */}
      <button
        type="button"
        onClick={toggleOpen}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary-container text-on-primary shadow-lg shadow-primary/30 z-50 flex items-center justify-center hover:scale-105 active:scale-95 transition-all duration-150 cursor-pointer"
        data-testid="chat-fab"
        aria-label="Ouvrir le chat"
      >
        <span className="material-symbols-outlined text-[28px]">
          {isOpen ? 'close' : 'chat'}
        </span>
        {unreadCount > 0 && !isOpen && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-error text-on-error text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>
    </>
  );
}
