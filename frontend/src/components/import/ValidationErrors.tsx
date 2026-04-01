import { useMemo } from 'react';
import { Badge } from '../ui/Badge';

interface ValidationError {
  sheet: string;
  row: number;
  column: string;
  message: string;
}

interface ValidationErrorsProps {
  errors: ValidationError[];
}

function CheckIcon() {
  return (
    <svg
      className="h-5 w-5 text-secondary"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={2}
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

function ErrorTable({ errors }: { errors: ValidationError[] }) {
  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full text-sm font-sans">
        <thead>
          <tr>
            <th className="px-4 py-3 text-sm font-medium text-on-surface-variant bg-surface-container text-right w-20">
              Ligne
            </th>
            <th className="px-4 py-3 text-sm font-medium text-on-surface-variant bg-surface-container text-left">
              Colonne
            </th>
            <th className="px-4 py-3 text-sm font-medium text-on-surface-variant bg-surface-container text-left">
              Message
            </th>
          </tr>
        </thead>
        <tbody>
          {errors.map((err, idx) => (
            <tr
              key={`${err.sheet}-${err.row}-${err.column}-${idx}`}
              className="bg-error-container/30"
            >
              <td className="px-4 py-3 text-sm font-medium text-on-surface text-right tabular-nums">
                {err.row}
              </td>
              <td className="px-4 py-3 text-sm text-on-surface-variant">
                {err.column}
              </td>
              <td className="px-4 py-3 text-sm text-error">
                {err.message}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ValidationErrors({ errors }: ValidationErrorsProps) {
  const groupedBySheet = useMemo(() => {
    const groups = new Map<string, ValidationError[]>();

    for (const error of errors) {
      const existing = groups.get(error.sheet);
      if (existing) {
        existing.push(error);
      } else {
        groups.set(error.sheet, [error]);
      }
    }

    return groups;
  }, [errors]);

  if (errors.length === 0) {
    return (
      <div className="flex items-center gap-2 py-6 justify-center">
        <CheckIcon />
        <Badge variant="success">Aucune erreur</Badge>
      </div>
    );
  }

  const sheets = Array.from(groupedBySheet.keys());
  const hasMultipleSheets = sheets.length > 1;

  if (!hasMultipleSheets) {
    return <ErrorTable errors={errors} />;
  }

  return (
    <div className="flex flex-col gap-6">
      {sheets.map((sheet) => {
        const sheetErrors = groupedBySheet.get(sheet);
        if (!sheetErrors) return null;

        return (
          <div key={sheet} className="flex flex-col gap-2">
            <h4 className="font-display text-base font-semibold text-on-surface px-4">
              {sheet}
              <span className="ml-2 text-sm font-normal text-on-surface-variant font-sans">
                ({sheetErrors.length} erreur{sheetErrors.length > 1 ? 's' : ''})
              </span>
            </h4>
            <ErrorTable errors={sheetErrors} />
          </div>
        );
      })}
    </div>
  );
}
