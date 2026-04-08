import { useState, useCallback } from 'react';

interface AudienceTargetingProps {
  targetSites: string[];
  targetDepartments: string[];
  targetShifts: string[];
  onSitesChange: (sites: string[]) => void;
  onDepartmentsChange: (departments: string[]) => void;
  onShiftsChange: (shifts: string[]) => void;
  availableSites?: { id: string; name: string }[];
}

function ChipInput({
  label,
  values,
  onChange,
  placeholder,
  icon,
}: {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
  placeholder: string;
  icon: string;
}) {
  const [input, setInput] = useState('');

  const handleAdd = useCallback(() => {
    const trimmed = input.trim();
    if (trimmed && !values.includes(trimmed)) {
      onChange([...values, trimmed]);
    }
    setInput('');
  }, [input, values, onChange]);

  const handleRemove = useCallback(
    (val: string) => {
      onChange(values.filter((v) => v !== val));
    },
    [values, onChange],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleAdd();
      }
    },
    [handleAdd],
  );

  return (
    <div>
      <label className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5">
        <span className="material-symbols-outlined text-xs align-middle mr-1">{icon}</span>
        {label}
      </label>
      <div className="flex flex-wrap gap-1.5 mb-2">
        {values.map((v) => (
          <span
            key={v}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium"
          >
            {v}
            <button
              type="button"
              onClick={() => handleRemove(v)}
              className="inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-primary/20 transition-colors"
            >
              <span className="material-symbols-outlined text-[12px]">close</span>
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-on-surface text-sm outline-none focus:ring-1 focus:ring-primary/20"
        />
        <button
          type="button"
          onClick={handleAdd}
          disabled={!input.trim()}
          className="px-3 py-2 rounded-lg bg-surface-container-lowest text-primary text-sm font-medium border border-outline-variant/15 hover:bg-primary/5 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <span className="material-symbols-outlined text-[16px]">add</span>
        </button>
      </div>
    </div>
  );
}

export function AudienceTargeting({
  targetSites,
  targetDepartments,
  targetShifts,
  onSitesChange,
  onDepartmentsChange,
  onShiftsChange,
  availableSites = [],
}: AudienceTargetingProps) {
  const [siteInput, setSiteInput] = useState('');

  const handleAddSite = useCallback(
    (siteId: string) => {
      if (siteId && !targetSites.includes(siteId)) {
        onSitesChange([...targetSites, siteId]);
      }
      setSiteInput('');
    },
    [targetSites, onSitesChange],
  );

  const handleRemoveSite = useCallback(
    (siteId: string) => {
      onSitesChange(targetSites.filter((s) => s !== siteId));
    },
    [targetSites, onSitesChange],
  );

  const getSiteName = useCallback(
    (id: string) => {
      const site = availableSites.find((s) => s.id === id);
      return site?.name ?? id;
    },
    [availableSites],
  );

  return (
    <div className="space-y-4">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
        <span className="material-symbols-outlined text-xs align-middle mr-1">groups</span>
        Ciblage audience
      </p>

      {/* Sites */}
      <div>
        <label className="block text-xs font-medium text-on-surface-variant mb-1.5">Sites</label>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {targetSites.map((id) => (
            <span
              key={id}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium"
            >
              {getSiteName(id)}
              <button
                type="button"
                onClick={() => handleRemoveSite(id)}
                className="inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-primary/20 transition-colors"
              >
                <span className="material-symbols-outlined text-[12px]">close</span>
              </button>
            </span>
          ))}
        </div>
        {availableSites.length > 0 ? (
          <select
            value={siteInput}
            onChange={(e) => {
              handleAddSite(e.target.value);
              e.target.value = '';
            }}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-on-surface text-sm outline-none focus:ring-1 focus:ring-primary/20 appearance-none"
          >
            <option value="">Sélectionner un site...</option>
            {availableSites
              .filter((s) => !targetSites.includes(s.id))
              .map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
          </select>
        ) : (
          <input
            type="text"
            value={siteInput}
            onChange={(e) => setSiteInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddSite(siteInput.trim());
              }
            }}
            placeholder="ID ou nom du site..."
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-on-surface text-sm outline-none focus:ring-1 focus:ring-primary/20"
          />
        )}
      </div>

      {/* Departments */}
      <ChipInput
        label="Départements"
        values={targetDepartments}
        onChange={onDepartmentsChange}
        placeholder="Ajouter un département..."
        icon="business"
      />

      {/* Shifts */}
      <ChipInput
        label="Équipes"
        values={targetShifts}
        onChange={onShiftsChange}
        placeholder="Ajouter une équipe..."
        icon="schedule"
      />
    </div>
  );
}
