interface Tab {
  key: string;
  label: string;
  badge?: number;
}

interface TabsProps {
  tabs: Tab[];
  activeKey: string;
  onChange: (key: string) => void;
}

export function Tabs({ tabs, activeKey, onChange }: TabsProps) {
  return (
    <div className="flex gap-6" role="tablist">
      {tabs.map((tab) => {
        const isActive = tab.key === activeKey;

        return (
          <button
            key={tab.key}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(tab.key)}
            className={[
              'relative pb-2.5 text-sm font-sans transition-colors duration-150 cursor-pointer',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-secondary/40 focus-visible:rounded-sm',
              isActive
                ? 'text-secondary font-medium'
                : 'text-on-surface-variant hover:text-on-surface',
            ].join(' ')}
          >
            <span className="flex items-center gap-2">
              {tab.label}
              {tab.badge !== undefined && tab.badge > 0 && (
                <span
                  className={[
                    'inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1.5 rounded-full text-xs font-medium font-sans',
                    isActive
                      ? 'bg-secondary-container text-on-secondary-container'
                      : 'bg-surface-container-high text-on-surface-variant',
                  ].join(' ')}
                >
                  {tab.badge}
                </span>
              )}
            </span>

            {isActive && (
              <span
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-secondary rounded-full"
                aria-hidden="true"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
