import { useMemo, type ReactNode } from 'react';

interface SheetPreviewProps {
  data: Record<string, unknown>[];
  maxRows?: number;
}

function formatCellValue(value: unknown): ReactNode {
  if (value === null || value === undefined) {
    return <span className="text-on-surface-variant/50">-</span>;
  }
  if (typeof value === 'boolean') {
    return value ? 'Oui' : 'Non';
  }
  if (typeof value === 'number') {
    return <span className="tabular-nums">{value}</span>;
  }
  return String(value);
}

export function SheetPreview({ data, maxRows = 20 }: SheetPreviewProps) {
  const columns = useMemo(() => {
    if (data.length === 0) return [];
    return Object.keys(data[0]);
  }, [data]);

  const visibleRows = useMemo(() => {
    return data.slice(0, maxRows);
  }, [data, maxRows]);

  const remainingCount = data.length - maxRows;

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center py-16">
        <p className="text-on-surface-variant text-sm font-sans">
          Aucune donnee
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="w-full overflow-x-auto">
        <table className="w-full text-sm font-sans">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-3 text-sm font-medium text-on-surface-variant bg-surface-container text-left whitespace-nowrap"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                className="transition-colors duration-150 hover:bg-surface-container-low"
              >
                {columns.map((col) => (
                  <td
                    key={col}
                    className="px-4 py-3 text-sm text-on-surface whitespace-nowrap max-w-[200px] truncate"
                  >
                    {formatCellValue(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {remainingCount > 0 && (
        <p className="text-sm text-on-surface-variant font-sans text-center py-2">
          ... et {remainingCount} ligne{remainingCount > 1 ? 's' : ''} supplementaire{remainingCount > 1 ? 's' : ''}
        </p>
      )}
    </div>
  );
}
