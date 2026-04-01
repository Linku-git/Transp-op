import { type ReactNode } from 'react';
import { Skeleton } from './Skeleton';

export interface Column<T> {
  key: string;
  label: string;
  align?: 'left' | 'right';
  render?: (row: T) => ReactNode;
}

type SortDirection = 'asc' | 'desc';

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  emptyMessage?: string;
  onSort?: (key: string) => void;
  sortKey?: string;
  sortDir?: SortDirection;
  rowKey?: (row: T, index: number) => string | number;
}

function SortIndicator({ active, dir }: { active: boolean; dir?: SortDirection }) {
  if (!active) return null;
  return (
    <span className="ml-1 text-on-surface-variant" aria-hidden="true">
      {dir === 'asc' ? '\u2191' : '\u2193'}
    </span>
  );
}

export function DataTable<T>({
  columns,
  data,
  isLoading = false,
  emptyMessage = 'No data available.',
  onSort,
  sortKey,
  sortDir,
  rowKey,
}: DataTableProps<T>) {
  const SKELETON_ROWS = 5;

  if (isLoading) {
    return (
      <div className="w-full overflow-x-auto">
        <table className="w-full text-sm font-sans">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={[
                    'px-4 py-3 text-sm font-medium text-on-surface-variant bg-surface-container',
                    col.align === 'right' ? 'text-right' : 'text-left',
                  ].join(' ')}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: SKELETON_ROWS }).map((_, rowIdx) => (
              <tr key={rowIdx}>
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3">
                    <Skeleton variant="text" className="w-3/4" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center py-16">
        <p className="text-on-surface-variant text-sm font-sans">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full text-sm font-sans">
        <thead>
          <tr>
            {columns.map((col) => {
              const isSorted = sortKey === col.key;
              return (
                <th
                  key={col.key}
                  className={[
                    'px-4 py-3 text-sm font-medium text-on-surface-variant bg-surface-container',
                    col.align === 'right' ? 'text-right' : 'text-left',
                    onSort ? 'cursor-pointer select-none' : '',
                  ].join(' ')}
                  onClick={onSort ? () => onSort(col.key) : undefined}
                  aria-sort={
                    isSorted
                      ? sortDir === 'asc'
                        ? 'ascending'
                        : 'descending'
                      : undefined
                  }
                >
                  {col.label}
                  <SortIndicator active={isSorted} dir={sortDir} />
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => {
            const key = rowKey ? rowKey(row, idx) : idx;
            return (
              <tr
                key={key}
                className="transition-colors duration-150 hover:bg-surface-container-low"
              >
                {columns.map((col) => {
                  const value = col.render
                    ? col.render(row)
                    : (row as Record<string, unknown>)[col.key];
                  return (
                    <td
                      key={col.key}
                      className={[
                        'px-4 py-3',
                        col.align === 'right'
                          ? 'text-right tabular-nums'
                          : 'text-left',
                      ].join(' ')}
                    >
                      {value as ReactNode}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
